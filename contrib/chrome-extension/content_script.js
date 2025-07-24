// content_script.js

console.log("Meet Controller: Content script injected and running.");

/**
 * A mapping of actions to their corresponding DOM element selectors.
 * These selectors are based on aria-labels, which are generally more stable
 * than class names but can still be changed by Google.
 * The 'i' flag makes the matching case-insensitive.
 */
const SELECTORS = {
  // Core Functions
  toggle_mute: '[data-is-muted]', // This is the most reliable selector for mute state.
  toggle_camera: '[data-is-muted][aria-label*="camera" i]',
  raise_hand: '[aria-label*="raise hand" i]',
  hang_up: '[aria-label*="leave call" i]',
  toggle_reactions: '[aria-label*="Send a reaction" i]',
  toggle_captions: '[aria-label*="Turn on captions" i], [aria-label*="Turn off captions" i]',
  leave_call: '[aria-label*="Leave call" i]',
  toggle_fullscreen: '[aria-label*="Enter full screen" i], [aria-label*="Exit full screen" i]',
  toggle_chat_panel: '[aria-label*="Show everyone" i]',
  toggle_participants_panel: '[aria-label*="Show everyone" i]',
  stop_sharing: '[aria-label*="Stop sharing" i]',

  // Reactions - These require opening a panel first.
  send_reaction_heart: '[aria-label*="💖"][role="button"]',
  send_reaction_thumb_up: '[aria-label*="👍"][role="button"]',
  send_reaction_celebrate: '[aria-label*="🎉"][role="button"]',
  send_reaction_clap: '[aria-label*="👏"][role="button"]',
  send_reaction_laugh: '[aria-label*="😂"][role="button"]',
  send_reaction_surprised: '[aria-label*="😮"][role="button"]',
  send_reaction_sad: '[aria-label*="😢"][role="button"]',
  send_reaction_thinking: '[aria-label*="🤔"][role="button"]',
  send_reaction_thumb_down: '[aria-label*="👎"][role="button"]',
  send_reaction_plus: '[aria-label*="➕"][role="button"]',
  send_reaction_crab: '[aria-label*="🦀"][role="button"]',
};

/**
 * Sends the current status of a control back to the native host.
 * @param {string} control - The name of the control (e.g., 'microphone', 'camera').
 * @param {boolean} is_on - The current state of the control.
 */
function sendStatus(control, is_on) {
  const statusMessage = {
    status: 'update',
    control: control,
    state: is_on ? 'on' : 'off'
  };
  console.log("Sending status:", statusMessage);
  chrome.runtime.sendMessage(statusMessage);
}

/**
 * Handles incoming commands from the background script.
 */
function handleCommand(message) {
  if (!message || !message.action) {
    return;
  }

  console.log("Received command:", message.action);
  const selector = SELECTORS[message.action];

  if (selector) {
    const element = document.querySelector(selector);
    if (element) {
      console.log(`Clicking element for action: ${message.action}`);
      element.click();
    } else {
      console.warn(`Element for action '${message.action}' not found with selector '${selector}'.`);
    }
  } else {
    console.warn(`No selector defined for action: ${message.action}`);
  }
}

/**
 * Uses a MutationObserver to watch for changes in the Meet UI and sync state.
 */
function setupStateObserver() {
  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      if (mutation.type === 'attributes' && mutation.target.hasAttribute('data-is-muted')) {
        const element = mutation.target;
        const isMuted = element.getAttribute('data-is-muted') === 'true';

        // Check if it's the mic or camera based on aria-label
        const ariaLabel = element.getAttribute('aria-label') || '';
        if (ariaLabel.toLowerCase().includes('microphone')) {
          sendStatus('microphone', !isMuted);
        } else if (ariaLabel.toLowerCase().includes('camera')) {
          sendStatus('camera', !isMuted);
        }
      }
      if (mutation.type === 'attributes' && mutation.attributeName === 'aria-pressed') {
        const element = mutation.target;
        const ariaLabel = element.getAttribute('aria-label') || '';
        const isPressed = element.getAttribute('aria-pressed') === 'true';

        if (ariaLabel.toLowerCase().includes('raise hand')) {
          sendStatus('hand', isPressed);
        } else if (ariaLabel.toLowerCase().includes('send a reaction')) {
          sendStatus('reactions', isPressed);
        }
      }
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-is-muted', 'aria-pressed'],
    subtree: true, // Watch all descendants of the body
  });
  console.log("Meet Controller: State observer is now active.");

  // Send initial status on load
  initialStatusCheck();
}

/**
 * Checks the initial state of the controls when the script loads.
 */
function initialStatusCheck() {
  console.log("Performing initial status check.");
  setTimeout(() => { // Give the UI a moment to fully load
    const micButton = document.querySelector(SELECTORS.toggle_mute);
    const camButton = document.querySelector(SELECTORS.toggle_camera);
    const handButton = document.querySelector(SELECTORS.raise_hand);

    if (micButton) {
      sendStatus('microphone', micButton.getAttribute('data-is-muted') === 'false');
    }
    if (camButton) {
      sendStatus('camera', camButton.getAttribute('data-is-muted') === 'false');
    }
    if (handButton) {
      sendStatus('hand', handButton.getAttribute('aria-pressed') === 'true');
    }
  }, 2000); // 2-second delay for safety
}

// Listen for messages (commands) from the background script.
chrome.runtime.onMessage.addListener(handleCommand);

// Start observing the page for state changes.
setupStateObserver();
