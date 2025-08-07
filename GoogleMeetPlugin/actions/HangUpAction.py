import os

from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class HangUpAction(MeetActionBase):
  """Action to hang up/leave the Google Meet call."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.action_name = "hang_up"

  def on_ready(self) -> None:
    """Sets the static icon for the hang up button."""
    icon_path = os.path.join(self.plugin_base.PATH, "assets", "hang_up.png")
    self.set_media(media_path=icon_path)

  def update_state(self, is_on: bool) -> None:
    """This action is stateless, so we do nothing."""
    pass
