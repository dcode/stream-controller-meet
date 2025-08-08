import { jest } from '@jest/globals';

global.chrome = {
  runtime: {
    connectNative: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
    },
    sendMessage: jest.fn(),
    lastError: undefined,
  },
  tabs: {
    query: jest.fn(),
    sendMessage: jest.fn(),
  },
  action: {
    setBadgeText: jest.fn(),
    setTitle: jest.fn(),
    setBadgeBackgroundColor: jest.fn(),
  },
  notifications: {
    create: jest.fn(),
    clear: jest.fn(),
  },
};

describe('Background Script', () => {
  let port;

  beforeEach(() => {
    jest.clearAllMocks();
    port = {
      onMessage: {
        addListener: jest.fn(),
      },
      onDisconnect: {
        addListener: jest.fn(),
      },
      postMessage: jest.fn(),
    };
    chrome.runtime.connectNative.mockReturnValue(port);
    // We need to use isolateModules to re-import the background script for each test
    // to reset its internal state.
    jest.isolateModules(() => {
      require('../background.mjs');
    });
  });

  it('should connect to the native host and set up listeners', () => {
    expect(chrome.runtime.connectNative).toHaveBeenCalledWith('com.github.dcode.stream_controller_meet');
    expect(port.onMessage.addListener).toHaveBeenCalled();
    expect(port.onDisconnect.addListener).toHaveBeenCalled();
  });

  it('should forward valid messages from native host to content script', () => {
    const message = { action: 'toggle_mute' };
    const [onMessageCallback] = port.onMessage.addListener.mock.calls[0];

    chrome.tabs.query.mockImplementation((query, callback) => {
      callback([{ id: 1 }]);
    });

    onMessageCallback(message);

    expect(chrome.tabs.query).toHaveBeenCalledWith({ url: 'https://meet.google.com/*', active: true }, expect.any(Function));
    expect(chrome.tabs.sendMessage).toHaveBeenCalledWith(1, message);
    expect(chrome.notifications.clear).toHaveBeenCalledWith('native-host-error-notification');
  });

  it('should not forward invalid messages from native host', () => {
    const invalidMessage = { action: 'invalid_action' };
    const [onMessageCallback] = port.onMessage.addListener.mock.calls[0];
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    onMessageCallback(invalidMessage);

    expect(chrome.tabs.sendMessage).not.toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Invalid message received from native host, discarding.',
      { message: invalidMessage, error: expect.any(Error) }
    );
    consoleErrorSpy.mockRestore();
  });

  it('should handle native host disconnection with an error and attempt to reconnect', () => {
    const [onDisconnectCallback] = port.onDisconnect.addListener.mock.calls[0];
    const errorMessage = 'Native host has exited.';
    chrome.runtime.lastError = { message: errorMessage };
    jest.useFakeTimers();
    const setTimeoutSpy = jest.spyOn(global, 'setTimeout');

    onDisconnectCallback();

    expect(chrome.notifications.create).toHaveBeenCalledWith(
      'native-host-error-notification',
      expect.objectContaining({
        title: 'Meet Controller Connection Error',
        message: expect.stringContaining(errorMessage),
      })
    );
    expect(chrome.action.setBadgeText).toHaveBeenCalledWith({ text: 'ERR' });
    expect(chrome.action.setTitle).toHaveBeenCalledWith({ title: `Error: ${errorMessage}` });

    // Test reconnect attempt
    expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 5000);

    setTimeoutSpy.mockRestore();
    jest.useRealTimers();
  });

  it('should handle clean native host disconnection', () => {
    const [onDisconnectCallback] = port.onDisconnect.addListener.mock.calls[0];
    chrome.runtime.lastError = undefined; // No error
    jest.useFakeTimers();
    const setTimeoutSpy = jest.spyOn(global, 'setTimeout');

    onDisconnectCallback();

    expect(chrome.action.setBadgeText).toHaveBeenCalledWith({ text: 'OFF' });
    expect(chrome.action.setTitle).toHaveBeenCalledWith({ title: 'Disconnected. Will attempt to reconnect.' });
    expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 5000);

    setTimeoutSpy.mockRestore();
    jest.useRealTimers();
  });


  it('should forward valid status updates from content script to native host', () => {
    const statusMessage = { status: 'update', control: 'microphone', state: 'on' };
    const [onMessageCallback] = chrome.runtime.onMessage.addListener.mock.calls[0];

    onMessageCallback(statusMessage);

    expect(port.postMessage).toHaveBeenCalledWith(statusMessage);
  });

  it('should not forward invalid status updates from content script', () => {
    const invalidStatusMessage = { status: 'update', control: 'invalid', state: 'on' };
    const [onMessageCallback] = chrome.runtime.onMessage.addListener.mock.calls[0];
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    onMessageCallback(invalidStatusMessage);

    expect(port.postMessage).not.toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Invalid status message from content script, not forwarding.',
      { message: invalidStatusMessage, error: expect.any(Error) }
    );
    consoleErrorSpy.mockRestore();
  });
});
