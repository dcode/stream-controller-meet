"""Unit tests for the action classes."""

from unittest.mock import MagicMock, patch

import pytest

from GoogleMeetPlugin.actions.HangUpAction import HangUpAction
from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase
from GoogleMeetPlugin.actions.RaiseHandAction import RaiseHandAction
from GoogleMeetPlugin.actions.ReactionActionBase import ReactionActionBase
from GoogleMeetPlugin.actions.SendHeartAction import SendHeartAction
from GoogleMeetPlugin.actions.SendThumbUpAction import SendThumbUpAction
from GoogleMeetPlugin.actions.ToggleCameraAction import ToggleCameraAction
from GoogleMeetPlugin.actions.ToggleChatPanelAction import ToggleChatPanelAction
from GoogleMeetPlugin.actions.ToggleMuteAction import ToggleMuteAction
from GoogleMeetPlugin.actions.ToggleParticipantsPanelAction import (
    ToggleParticipantsPanelAction,
)
from GoogleMeetPlugin.actions.TogglePresentAction import TogglePresentAction


@pytest.fixture
def mock_plugin_base():
    """Fixture to create a mock plugin base."""
    plugin = MagicMock()
    plugin.PATH = "some/path"
    return plugin


def test_meet_action_base_on_key_down(mock_plugin_base):
    """Test that on_key_down sends the correct command."""
    action = MeetActionBase()
    action.plugin_base = mock_plugin_base
    action.action_name = "test_action_name"
    action.on_key_down()
    mock_plugin_base.send_command.assert_called_once_with(action="test_action_name")


def test_meet_action_base_update_state(mock_plugin_base):
    """Test that update_state updates the icon."""
    action = MeetActionBase()
    action.plugin_base = mock_plugin_base
    action.icon_on = "icon_on.png"
    action.icon_off = "icon_off.png"
    action.set_media = MagicMock()
    action.update_state(True)
    action.set_media.assert_called_once_with(media_path="some/path/assets/icon_on.png")
    action.set_media.reset_mock()
    action.update_state(False)
    action.set_media.assert_called_once_with(media_path="some/path/assets/icon_off.png")


def test_reaction_action_base_update_state(mock_plugin_base):
    """Test that update_state is a no-op for reaction actions."""
    action = ReactionActionBase()
    action.plugin_base = mock_plugin_base
    action.set_media = MagicMock()
    action.update_state(True)
    action.set_media.assert_not_called()
