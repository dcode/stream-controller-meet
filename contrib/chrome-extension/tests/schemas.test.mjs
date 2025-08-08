
import { ActionCommandSchema, StatusUpdateSchema, ErrorSchema, ActionType } from '../schemas.mjs';

describe('Schemas', () => {
  describe('ActionType', () => {
    it('should contain all expected action types', () => {
      const expectedActions = [
        "toggle_mute", "toggle_camera", "raise_hand", "hang_up", "toggle_reactions",
        "toggle_present", "toggle_captions", "leave_call", "toggle_fullscreen",
        "toggle_chat_panel", "toggle_participants_panel", "stop_sharing",
        "send_reaction_heart", "send_reaction_thumb_up", "send_reaction_celebrate",
        "send_reaction_clap", "send_reaction_laugh", "send_reaction_surprised",
        "send_reaction_sad", "send_reaction_thinking", "send_reaction_thumb_down",
        "send_reaction_plus", "send_reaction_crab"
      ];
      expect(ActionType.options).toEqual(expect.arrayContaining(expectedActions));
      expect(expectedActions).toEqual(expect.arrayContaining(ActionType.options));
    });
  });

  describe('ActionCommandSchema', () => {
    it('should validate a correct action command', () => {
      const validCommand = { action: 'toggle_mute' };
      expect(() => ActionCommandSchema.parse(validCommand)).not.toThrow();
    });

    it('should invalidate an incorrect action command', () => {
      const invalidCommand = { action: 'invalid_action' };
      expect(() => ActionCommandSchema.parse(invalidCommand)).toThrow();
    });

    it('should invalidate a command with extra properties', () => {
      const invalidCommand = { action: 'toggle_mute', extra: 'property' };
       expect(() => ActionCommandSchema.parse(invalidCommand)).toThrow();
    });
  });

  describe('StatusUpdateSchema', () => {
    it('should validate a correct status update', () => {
      const validUpdate = { status: 'update', control: 'microphone', state: 'on' };
      expect(() => StatusUpdateSchema.parse(validUpdate)).not.toThrow();
    });

    it('should invalidate a status update with an invalid control', () => {
      const invalidUpdate = { status: 'update', control: 'invalid_control', state: 'on' };
      expect(() => StatusUpdateSchema.parse(invalidUpdate)).toThrow();
    });

    it('should invalidate a status update with an invalid state', () => {
      const invalidUpdate = { status: 'update', control: 'microphone', state: 'invalid_state' };
      expect(() => StatusUpdateSchema.parse(invalidUpdate)).toThrow();
    });
  });

  describe('ErrorSchema', () => {
    it('should validate a correct error message', () => {
      const validError = { status: 'error', message: 'An error occurred' };
      expect(() => ErrorSchema.parse(validError)).not.toThrow();
    });

    it('should invalidate an error message with a missing message', () => {
      const invalidError = { status: 'error' };
      expect(() => ErrorSchema.parse(invalidError)).toThrow();
    });
  });
});
