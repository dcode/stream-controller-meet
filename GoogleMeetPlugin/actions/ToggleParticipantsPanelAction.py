from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class ToggleParticipantsPanelAction(MeetActionBase):
  """Action to toggle the participants panel in Google Meet."""

  def __init__(self, *args, **kwargs):
    """Initializes a new ToggleParticipantsPanelAction."""
    super().__init__(*args, **kwargs)
    self.action_name = "toggle_participants_panel"
    self.icon_on = "participants_on.png"
    self.icon_off = "participants_off.png"
    self.icon_unknown = "participants_unknown.png"

  def on_ready(self) -> None:
    """
    Called when the action is added to the deck.
    The initial icon is set by the base class.
    """
    super().on_ready()
