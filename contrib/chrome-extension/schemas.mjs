/**
 * @file Zod schemas for validating messages between the extension and the native host.
 * These schemas should be kept in sync with the Pydantic models in `models.py`.
 */

import { z } from './lib/zod.min.mjs';

export const ActionType = z.enum([
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
]);

export const ActionCommandSchema = z.object({
  action: ActionType,
}).strict();

export const StatusUpdateSchema = z.object({
  status: z.literal("update"),
  control: z.enum(["microphone", "camera", "hand", "reactions", "call", "presenting", "chat_panel", "participants_panel"]),
  state: z.enum(["on", "off"]),
}).strict();

export const ErrorSchema = z.object({
  status: z.literal("error"),
  message: z.string(),
}).strict();
