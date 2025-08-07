// background.js

import { ActionCommandSchema, StatusUpdateSchema } from './schemas.mjs';

// The name of the native messaging host.
// This must match the name in the native host manifest file.
const nativeHostName = "com.github.dcode.stream_controller_meet";
const NOTIFICATION_ID = "native-host-error-notification";

let port;

console.log("Meet Controller Bridge: Background script started.");

function connect() {
    console.log(`Attempting to connect to native host: ${nativeHostName}`);
    port = chrome.runtime.connectNative(nativeHostName);

    port.onMessage.addListener((message) => {
        try {
            // Validate the incoming command from the native host
            ActionCommandSchema.parse(message);
            console.log("Received valid message from native host:", message);

            // Connection is working, clear any error indicators.
            chrome.notifications.clear(NOTIFICATION_ID);
            chrome.action.setBadgeText({ text: '' });
            chrome.action.setTitle({ title: 'Meet Controller Bridge (Connected)' });

            // Forward the message to the content script in the active Google Meet tab.
            chrome.tabs.query({ url: "https://meet.google.com/*", active: true }, (tabs) => {
                if (tabs.length > 0) {
                    chrome.tabs.sendMessage(tabs[0].id, message);
                }
            });
        } catch (e) {
            console.error("Invalid message received from native host, discarding.", { message, error: e });
        }
    });

    port.onDisconnect.addListener(() => {
        const error = chrome.runtime.lastError;
        if (error) {
            console.error("Native host disconnected with error:", error.message);
            // Provide feedback to the user.
            const errorMessage = `Failed to connect to the native host. Make sure the StreamController plugin is running and the host is installed correctly. Error: ${error.message}`;

            // 1. Show a system notification
            chrome.notifications.create(NOTIFICATION_ID, {
                type: 'basic',
                iconUrl: 'icon.png',
                title: 'Meet Controller Connection Error',
                message: errorMessage,
                priority: 2
            });

            // 2. Set a persistent error badge on the extension icon
            chrome.action.setBadgeBackgroundColor({ color: '#D93025' }); // Google Red
            chrome.action.setBadgeText({ text: 'ERR' });
            chrome.action.setTitle({ title: `Error: ${error.message}` });
        } else {
            console.log("Native host disconnected cleanly.");
            // Indicate a disconnected state on the badge.
            chrome.action.setBadgeBackgroundColor({ color: '#808080' }); // Grey
            chrome.action.setBadgeText({ text: 'OFF' });
            chrome.action.setTitle({ title: 'Disconnected. Will attempt to reconnect.' });
        }
        port = null;
        // Attempt to reconnect after a delay.
        setTimeout(connect, 5000);
    });
}

// Listen for status updates from the content script.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (port && message.status === 'update') {
        try {
            // Validate the outgoing status update from the content script
            StatusUpdateSchema.parse(message);
            console.log("Received valid status from content script:", message);
            port.postMessage(message);
        } catch (e) {
            console.error("Invalid status message from content script, not forwarding.", { message, error: e });
        }
    } else if (!port) {
        console.log("Received message from content script, but port is not connected.");
        // The onDisconnect handler will be managing the UI feedback.
    }
    // Return true to indicate you wish to send a response asynchronously.
    return true;
});

// Initial connection attempt.
connect();
