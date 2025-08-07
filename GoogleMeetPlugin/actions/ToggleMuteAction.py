from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class ToggleMuteAction(MeetActionBase):
  """Action to toggle the microphone in Google Meet."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.action_name = "toggle_mute"
    self.icon_on = "mic_on.png"  # Icon when mic is unmuted
    self.icon_off = "mic_off.png"  # Icon when mic is muted
    self.icon_unknown = "mic_unknown.png"
