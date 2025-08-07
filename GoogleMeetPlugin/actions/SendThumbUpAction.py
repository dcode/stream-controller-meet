from GoogleMeetPlugin.actions.ReactionActionBase import ReactionActionBase


class SendThumbUpAction(ReactionActionBase):
  """Action to send a 'Thumb Up' reaction."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.action_name = "send_reaction_thumb_up"
    self.icon_name = "reaction_thumb_up.png"
