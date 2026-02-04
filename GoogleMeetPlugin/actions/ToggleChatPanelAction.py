from GoogleMeetPlugin.actions.MeetActionBase import MeetActionBase


class ToggleChatPanelAction(MeetActionBase):
  """Action to toggle the chat panel in Google Meet."""

  def __init__(self, *args, **kwargs):
    """Initializes a new ToggleChatPanelAction."""
    super().__init__(*args, **kwargs)
    self.action_name = "toggle_chat_panel"
    self.icon_on = "chat_on.png"
    self.icon_off = "chat_off.png"
    self.icon_unknown = "chat_unknown.png"

  def on_ready(self) -> None:
    """
    Called when the action is added to the deck.
    The initial icon is set by the base class.
    """
    super().on_ready()
