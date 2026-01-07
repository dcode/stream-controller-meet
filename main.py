# Import StreamController modules
import logging
import os
import sys

# Import python modules
import threading
from typing import Any

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

from pydantic import ValidationError
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

# Import actions
from GoogleMeetPlugin.actions.HangUpAction import HangUpAction
from GoogleMeetPlugin.actions.RaiseHandAction import RaiseHandAction
from GoogleMeetPlugin.actions.SendHeartAction import SendHeartAction
from GoogleMeetPlugin.actions.SendThumbUpAction import SendThumbUpAction
from GoogleMeetPlugin.actions.ToggleCameraAction import ToggleCameraAction
from GoogleMeetPlugin.actions.ToggleChatPanelAction import ToggleChatPanelAction
from GoogleMeetPlugin.actions.ToggleMuteAction import ToggleMuteAction
from GoogleMeetPlugin.actions.ToggleParticipantsPanelAction import (
  ToggleParticipantsPanelAction,
)
from GoogleMeetPlugin.actions.TogglePresentAction import TogglePresentAction
from GoogleMeetPlugin.models import ActionCommand, StatusUpdate
from GoogleMeetPlugin.socket_ipc import SocketIPCServer

# Setup logging
logger = logging.getLogger(__name__)


class GoogleMeetPlugin(PluginBase):
  """A StreamController plugin to control Google Meet via a Chrome extension.

  This plugin uses native messaging to communicate with a companion Chrome
  extension, allowing for control of Meet functions and receiving status
  updates to display on the Stream Deck.
  """

  def __init__(self) -> None:
    """Initializes the GoogleMeetPlugin."""
    super().__init__()

    # Define the socket path according to XDG specs for Flatpak compatibility
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR", "/tmp")
    socket_dir = os.path.join(
      xdg_runtime_dir, "app/com.core477.StreamController"
    )
    socket_path = os.path.join(socket_dir, "meet_plugin.sock")

    # Setup and start the socket server in a background thread
    # The proxy process launched by Chrome will connect to this.
    self.ipc_server = SocketIPCServer(socket_path, self.handle_status_update)
    self.ipc_thread = threading.Thread(
      target=self.ipc_server.listen, daemon=True
    )
    self.ipc_thread.start()
    logger.info(f"Google Meet plugin initialized, listening on {socket_path}.")

    # Register all available actions
    self._register_actions()

    # Register plugin
    self.register(
      plugin_name="Google Meet",
      github_repo="https://github.com/dcode/streamdeck-meet",
      plugin_version="1.0.0",
      app_version="1.1.1-alpha",
    )

  def _register_actions(self) -> None:
    """Creates and registers all ActionHolders for the plugin."""
    action_definitions = {
      "toggle_mute": {"class": ToggleMuteAction, "name": "Toggle Mute"},
      "toggle_camera": {"class": ToggleCameraAction, "name": "Toggle Camera"},
      "raise_hand": {"class": RaiseHandAction, "name": "Raise Hand"},
      "hang_up": {"class": HangUpAction, "name": "Hang Up"},
      "toggle_present": {
        "class": TogglePresentAction,
        "name": "Toggle Present",
      },
      "send_reaction_thumb_up": {"class": SendThumbUpAction, "name": "Send 👍"},
      "send_reaction_heart": {"class": SendHeartAction, "name": "Send ❤️"},
      "toggle_chat_panel": {
        "class": ToggleChatPanelAction,
        "name": "Toggle Chat",
      },
      "toggle_participants_panel": {
        "class": ToggleParticipantsPanelAction,
        "name": "Toggle Participants",
      },
    }

    for action_key, details in action_definitions.items():
      action_holder = ActionHolder(
        plugin_base=self,
        action_base=details["class"],
        action_id=f"com.github.dcode.streamdeck-meet.{action_key}",
        action_name=details["name"],
      )
      self.add_action_holder(action_holder)

  def send_command(self, action: str) -> None:
    """
    Sends a command to the Chrome extension.

    Args:
        action: The action name to be sent (e.g., 'toggle_mute').
    """
    command = ActionCommand(action=action)
    self.ipc_server.send_message(command.model_dump())

  def handle_hang_up(self) -> None:
    """
    Called when the Google Meet call has ended. Resets the state of all
    toggleable actions on the Stream Deck to their default 'off' state.
    """
    logger.info("Call ended. Resetting action states.")
    if not self.main_view:
      return

    # List of action keys that are stateful and should be reset.
    resettable_action_keys = [
      "toggle_mute",
      "toggle_camera",
      "raise_hand",
      "toggle_present",
      "toggle_chat_panel",
      "toggle_participants_panel",
    ]

    for deck in self.main_view.deck_controller.decks.values():
      for action_instance in deck.actions.values():
        for key in resettable_action_keys:
          if action_instance.action_id.endswith(key):
            # Reset to default 'off' state
            action_instance.update_state(False)
            break  # Move to the next action instance

  def handle_status_update(self, message: dict[str, Any]) -> None:
    """
    Callback function to handle status updates from the extension.

    This function is called by the NativeMessagingHandler from its thread.
    It finds the relevant action instances on all connected decks and
    updates their state.

    Args:
        message: The status message received from the extension.
    """
    try:
      status = StatusUpdate.model_validate(message)
    except ValidationError as e:
      logger.warning(f"Received invalid status message: {e}")
      return

    logger.info(f"Received status update: {status}")
    control = status.control
    state = status.state

    if control == "call" and state == "off":
      self.handle_hang_up()
      return

    action_map = {
      "microphone": "toggle_mute",
      "camera": "toggle_camera",
      "hand": "raise_hand",
      "presenting": "toggle_present",
      "chat_panel": "toggle_chat_panel",
      "participants_panel": "toggle_participants_panel",
      # 'reactions' has a status but no corresponding resettable action state
      # in the same way. It's a toggle for a panel.
    }

    action_key = action_map.get(control)
    if not action_key or not self.main_view:
      return

    # Find all instances of this action across all decks and update their state
    for deck in self.main_view.deck_controller.decks.values():
      for action_instance in deck.actions.values():
        if action_instance.action_id.endswith(action_key):
          action_instance.update_state(status.state == "on")
