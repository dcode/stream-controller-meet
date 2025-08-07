"""
Unit tests for the main GoogleMeetPlugin class.
"""

from unittest.mock import MagicMock, patch

import pytest

# Thanks to conftest.py, we can now import this without errors
from main import GoogleMeetPlugin


@pytest.fixture
def plugin(mocker):
  """A fixture to create a fresh plugin instance for each test."""
  # Mock the SocketIPCServer so we don't deal with real sockets
  mocker.patch("main.SocketIPCServer")
  # Mock the threading so we don't create real threads
  mocker.patch("main.threading.Thread")
  return GoogleMeetPlugin()


def test_plugin_initialization(mocker):
  """Test that the plugin initializes correctly."""
  mock_socket_server_cls = mocker.patch("main.SocketIPCServer")
  mock_thread_cls = mocker.patch("main.threading.Thread")
  mock_register_actions = mocker.patch(
    "main.GoogleMeetPlugin._register_actions"
  )

  plugin_instance = GoogleMeetPlugin()

  # Assert that the socket server was created with the correct path and callback
  mock_socket_server_cls.assert_called_once_with(
    mocker.ANY, plugin_instance.handle_status_update
  )
  assert "meet_plugin.sock" in mock_socket_server_cls.call_args[0][0]

  # Assert that the listening thread was created and started
  mock_thread_cls.assert_called_once_with(
    target=plugin_instance.ipc_server.listen, daemon=True
  )
  plugin_instance.ipc_thread.start.assert_called_once()

  # Assert that actions were registered
  mock_register_actions.assert_called_once()


def test_send_command(plugin: GoogleMeetPlugin):
  """Test that commands are correctly formatted and sent."""
  plugin.send_command(action="toggle_mute")

  plugin.ipc_server.send_message.assert_called_once_with(
    {"action": "toggle_mute"}
  )


def test_handle_status_update_toggles_action(plugin: GoogleMeetPlugin):
  """Test that a status update correctly finds and updates an action."""
  # Setup a mock action instance that would exist on a deck
  mock_action = MagicMock()
  mock_action.action_id = "com.github.dcode.streamdeck-meet.toggle_camera"
  plugin.main_view.deck_controller.decks = {
    "deck1": MagicMock(actions={"key1": mock_action})
  }

  status_message = {"status": "update", "control": "camera", "state": "on"}
  plugin.handle_status_update(status_message)

  mock_action.update_state.assert_called_once_with(True)


def test_handle_hang_up_resets_actions(plugin: GoogleMeetPlugin):
  """Test that the hang up event resets all stateful actions."""
  mock_mute_action = MagicMock()
  mock_mute_action.action_id = "com.github.dcode.streamdeck-meet.toggle_mute"
  mock_hangup_action = MagicMock()
  mock_hangup_action.action_id = (
    "com.github.dcode.streamdeck-meet.hang_up"  # Should not be reset
  )

  plugin.main_view.deck_controller.decks = {
    "deck1": MagicMock(
      actions={"key1": mock_mute_action, "key2": mock_hangup_action}
    )
  }

  plugin.handle_hang_up()

  # Assert that the stateful action was reset
  mock_mute_action.update_state.assert_called_once_with(False)
  # Assert that the stateless action was not touched
  mock_hangup_action.update_state.assert_not_called()


def test_handle_invalid_status_update(plugin: GoogleMeetPlugin, caplog):
  """Test that an invalid message is logged and ignored."""
  # Setup a mock action to ensure it's NOT called
  mock_action = MagicMock()
  mock_action.action_id = "com.github.dcode.streamdeck-meet.toggle_camera"
  plugin.main_view.deck_controller.decks = {
    "deck1": MagicMock(actions={"key1": mock_action})
  }

  invalid_message = {"foo": "bar"}  # Missing required fields
  plugin.handle_status_update(invalid_message)

  assert "Received invalid status message" in caplog.text
  # Assert that no action's state was updated
  mock_action.update_state.assert_not_called()
