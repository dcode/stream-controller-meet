import os

from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class ReactionActionBase(MeetActionBase):
  """
  A base class for stateless reaction actions.
  These actions send a specific reaction and have a static icon.
  """

  def __init__(self, *args, **kwargs):
    """Initializes a new ReactionActionBase."""
    super().__init__(*args, **kwargs)
    self.icon_name: str = ""  # To be overridden by subclasses

  def on_ready(self) -> None:
    """Sets the static icon for the reaction button."""
    if self.icon_name:
      icon_path = os.path.join(self.plugin_base.PATH, "assets", self.icon_name)
      self.set_media(media_path=icon_path)

  def update_state(self, is_on: bool) -> None:
    """This action is stateless, so we do nothing."""
    pass
