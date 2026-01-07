"""Pydantic models for validating the IPC messages.

This module defines the Pydantic models used to validate the structure and
content of messages exchanged between the plugin and the Chrome extension proxy.
"""

from typing import Literal

from pydantic import BaseModel, Field

# Define all possible actions that can be sent to the Chrome extension.
# These correspond to the keys in the SELECTORS object in content_script.js.
ActionType = Literal[
  "toggle_mute",
  "toggle_camera",
  "raise_hand",
  "hang_up",
  "toggle_reactions",
  "toggle_present",
  "toggle_captions",
  "leave_call",
  "toggle_fullscreen",
  "toggle_chat_panel",
  "toggle_participants_panel",
  "stop_sharing",
  "send_reaction_heart",
  "send_reaction_thumb_up",
  "send_reaction_celebrate",
  "send_reaction_clap",
  "send_reaction_laugh",
  "send_reaction_surprised",
  "send_reaction_sad",
  "send_reaction_thinking",
  "send_reaction_thumb_down",
  "send_reaction_plus",
  "send_reaction_crab",
]


class ActionCommand(BaseModel):
  """A command sent from the plugin to the Chrome extension."""

  action: ActionType = Field(
    ..., description="The action to be performed in Google Meet."
  )


# Define the types of controls whose status can be reported by the extension.
ControlType = Literal[
  "microphone",
  "camera",
  "hand",
  "reactions",
  "call",
  "presenting",
  "chat_panel",
  "participants_panel",
]

# Define the possible states for a control.
ControlState = Literal["on", "off"]


class StatusUpdate(BaseModel):
  """A status update sent from the Chrome extension to the plugin."""

  status: Literal["update"] = Field(
    ..., description="The type of message, always 'update' for status changes."
  )
  control: ControlType = Field(..., description="The UI control that changed.")
  state: ControlState = Field(..., description="The new state of the control.")
