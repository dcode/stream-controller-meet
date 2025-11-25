from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class ToggleCameraAction(MeetActionBase):
  """Action to toggle the camera in Google Meet."""

  def __init__(self, *args, **kwargs):
    """Initializes a new ToggleCameraAction."""
    super().__init__(*args, **kwargs)
    self.action_name = "toggle_camera"
    self.icon_on = "camera_on.png"
    self.icon_off = "camera_off.png"
    self.icon_unknown = "camera_unknown.png"
