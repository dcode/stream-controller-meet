from .MeetActionBase import MeetActionBase


class RaiseHandAction(MeetActionBase):
  """Action to raise or lower hand in Google Meet."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.action_name = "raise_hand"
    self.icon_on = "hand_raised.png"  # Icon when hand is up
    self.icon_off = "hand_lowered.png"  # Icon when hand is down
    self.icon_unknown = "hand_unknown.png"
