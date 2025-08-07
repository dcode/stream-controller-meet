from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class TogglePresentAction(MeetActionBase):
  """Action to toggle screen sharing in Google Meet."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.action_name = "toggle_present"
    self.icon_on = "present_on.png"
    self.icon_off = "present_off.png"
    self.icon_unknown = "present_unknown.png"

  def on_ready(self) -> None:
    """
    Called when the action is added to the deck.
    The initial icon is set by the base class.
    """
    super().on_ready()
