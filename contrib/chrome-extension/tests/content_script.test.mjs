/**
 * @jest-environment jsdom
 */
import { jest } from '@jest/globals';
import { handleCommand, sendStatus, handleReactionCommand } from '../content_script.mjs';

global.chrome = {
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
        addListener: jest.fn()
    }
  },
};

describe('Content Script', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = `
      <div data-is-muted="true" aria-label="microphone is muted"></div>
      <div data-is-muted="true" aria-label="camera is off"></div>
      <div aria-label="raise hand"></div>
      <div aria-label="leave call"></div>
      <div aria-label="Present now"></div>
      <div aria-label="Send a reaction"></div>
      <div aria-label="Turn on captions"></div>
      <div aria-label="Chat with everyone"></div>
      <div aria-label="Show everyone" role="button"></div>
    `;
  });

  it('should click the correct element for a given action', () => {
    const muteButton = document.querySelector('[data-is-muted][aria-label*="microphone"]');
    const clickSpy = jest.spyOn(muteButton, 'click');

    handleCommand({ action: 'toggle_mute' });

    expect(clickSpy).toHaveBeenCalled();
  });

  it('should send the correct status message', () => {
    sendStatus('microphone', true);
    expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
      status: 'update',
      control: 'microphone',
      state: 'on',
    });

    sendStatus('camera', false);
    expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
      status: 'update',
      control: 'camera',
      state: 'off',
    });
  });

  it('should handle reaction commands', async () => {
    jest.useFakeTimers();
    document.body.innerHTML += `<div aria-label="💖" role="button"></div>`;

    const reactionButton = document.querySelector('[aria-label*="💖"]');
    const clickSpy = jest.spyOn(reactionButton, 'click');

    const reactionPromise = handleReactionCommand('send_reaction_heart', '[aria-label*="💖"][role="button"]');

    // Advance timers to allow the first setTimeout to resolve
    jest.advanceTimersByTime(250);

    await reactionPromise;

    expect(clickSpy).toHaveBeenCalled();

    // Advance timers to allow the second setTimeout to resolve
    jest.advanceTimersByTime(500);

    jest.useRealTimers();
  });
});