// background.js

// The name of the native messaging host.
// This must match the name in the native host manifest file.
const nativeHostName = "com.github.dcode.stream_controller_meet";

let port;

console.log("Meet Controller Bridge: Background script started.");

function connect() {
    console.log(`Attempting to connect to native host: ${nativeHostName}`);
    port = chrome.runtime.connectNative(nativeHostName);

    port.onMessage.addListener((message) => {
        console.log("Received message from native host:", message);
        // Forward the message to the content script in the active Google Meet tab.
        chrome.tabs.query({ url: "https://meet.google.com/*", active: true }, (tabs) => {
            if (tabs.length > 0) {
                chrome.tabs.sendMessage(tabs[0].id, message);
            } else {
                console.log("No active Google Meet tab found.");
            }
        });
    });

    port.onDisconnect.addListener(() => {
        const error = chrome.runtime.lastError;
        if (error) {
            console.error("Native host disconnected:", error.message);
        } else {
            console.log("Native host disconnected.");
        }
        port = null;
        // Optional: Attempt to reconnect after a delay.
        setTimeout(connect, 5000);
    });
}

// Listen for status updates from the content script.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (port && message.status) {
        console.log("Received status from content script:", message);
        // Forward the status update to the native host.
        port.postMessage(message);
    } else {
        console.log("Received message from content script, but port is not connected.");
    }
    // Return true to indicate you wish to send a response asynchronously.
    return true;
});

// Initial connection attempt.
connect();
