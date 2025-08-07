from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from src.backend.PluginManager.ActionBase import ActionBase

if TYPE_CHECKING:
  from main import GoogleMeetPlugin


class MeetActionBase(ActionBase):
  """A base class for Google Meet actions providing common functionality."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.plugin_base: GoogleMeetPlugin
    self.is_on: Optional[bool] = None  # None means unknown state
    self.action_name: str = "base_action"  # To be overridden by subclasses
    self.icon_on: str = ""
    self.icon_off: str = ""
    self.icon_unknown: str = ""

  def on_ready(self) -> None:
    """Called when the action is added to the deck. Sets the initial icon."""
    self.set_initial_icon()

  def on_key_down(self) -> None:
    """Called when the key is pressed. Sends the command to the plugin."""
    self.plugin_base.send_command(action=self.action_name)

  def set_initial_icon(self) -> None:
    """Sets the icon based on the initial (unknown) state."""
    if self.icon_unknown:
      icon_path = os.path.join(
        self.plugin_base.PATH, "assets", self.icon_unknown
      )
      self.set_media(media_path=icon_path)

  def update_state(self, is_on: bool) -> None:
    """Updates the action's state and icon based on feedback from the extension."""
    if self.is_on == is_on:
      return  # No change

    self.is_on = is_on
    icon_name = self.icon_on if self.is_on else self.icon_off
    icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)
    self.set_media(media_path=icon_path)
