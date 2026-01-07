from GoogleMeetPlugin.actions.ReactionActionBase import ReactionActionBase


class SendHeartAction(ReactionActionBase):
  """Action to send a 'Heart' reaction."""

  def __init__(self, *args, **kwargs):
    """Initializes a new SendHeartAction."""
    super().__init__(*args, **kwargs)
    self.action_name = "send_reaction_heart"
    self.icon_name = "reaction_heart.png"
