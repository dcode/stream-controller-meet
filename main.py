# Import StreamController modules
import logging

# Import python modules
import threading
from typing import Any, Dict

from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.PluginBase import PluginBase

from .actions.HangUpAction import HangUpAction
from .actions.RaiseHandAction import RaiseHandAction
from .actions.ToggleCameraAction import ToggleCameraAction
# Import actions
from .actions.ToggleMuteAction import ToggleMuteAction
# Import local modules
from .socket_ipc import SocketIPCServer

# Setup logging
logger = logging.getLogger(__name__)


class GoogleMeetPlugin(PluginBase):
  """
      A StreamController plugin to control Google Meet via a Chrome extension.

      This plugin uses native messaging to communicate with a companion Chrome
      extension, allowing for control of Meet functions and receiving status
     updates to display on the Stream Deck.
  """

  def __init__(self) -> None:
    super().__init__()

    # Setup and start the socket server in a background thread
    # The proxy process launched by Chrome will connect to this.
    self.ipc_server = SocketIPCServer(
        "127.0.0.1", 35677, self.handle_status_update
    )
    self.ipc_thread = threading.Thread(target=self.ipc_server.listen, daemon=True)
    self.ipc_thread.start()
    logger.info("Google Meet plugin initialized.")

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
    self.ipc_server.send_message({"action": action})

  def handle_status_update(self, message: Dict[str, Any]) -> None:
    """
    Callback function to handle status updates from the extension.

    This function is called by the NativeMessagingHandler from its thread.
    It finds the relevant action instances on all connected decks and
    updates their state.

    Args:
        message: The status message received from the extension.
    """
    logger.info(f"Received status update: {message}")
    control = message.get("control")
    state = message.get("state")

    action_map = {
      "microphone": "toggle_mute",
      "camera": "toggle_camera",
      "hand": "raise_hand",
    }

    action_key = action_map.get(control)
    if not action_key or not self.main_view:
      return

    # Find all instances of this action across all decks and update their state
    for deck in self.main_view.deck_controller.decks.values():
      for action_instance in deck.actions.values():
        if action_instance.action_id.endswith(action_key):
          action_instance.update_state(state == "on")
