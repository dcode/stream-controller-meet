// content_script.js

console.log("Meet Controller: Content script injected and running.");

let lastKnownPresentingState = false;
let inCall = false; // Global state to track if we are in a call

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
  toggle_present: '[aria-label*="Present now" i], [aria-label*="Stop presenting" i]',
  toggle_reactions: '[aria-label*="Send a reaction" i]',
  toggle_captions: '[aria-label*="Turn on captions" i], [aria-label*="Turn off captions" i]',
  leave_call: '[aria-label*="Leave call" i]',
  toggle_fullscreen: '[aria-label*="Enter full screen" i], [aria-label*="Exit full screen" i]',
  toggle_chat_panel: '[aria-label*="Chat with everyone" i]',
  toggle_participants_panel: '[aria-label*="Show everyone" i][role="button"]',
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
  // The background script is the single point of contact with the native host,
  // so we'll let it handle all validation before sending messages.
  console.log("Sending status:", statusMessage);
  chrome.runtime.sendMessage(statusMessage);
}

/**
 * Handles commands to send a specific reaction. It will open the reaction
 * panel if it's closed, click the reaction, and then close the panel.
 * @param {string} action - The reaction action name.
 * @param {string} reactionSelector - The DOM selector for the reaction button.
 */
async function handleReactionCommand(action, reactionSelector) {
  const reactionsToggleButton = document.querySelector(SELECTORS.toggle_reactions);
  if (!reactionsToggleButton) {
    console.warn("Could not find the main 'Send a reaction' button.");
    return;
  }

  const wasPanelOpen = reactionsToggleButton.getAttribute('aria-pressed') === 'true';

  if (!wasPanelOpen) {
    // Open the panel
    reactionsToggleButton.click();
    // Wait a moment for the panel to animate and become available
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  const reactionElement = document.querySelector(reactionSelector);
  if (reactionElement) {
    console.log(`Clicking reaction element for action: ${action}`);
    reactionElement.click();
  } else {
    console.warn(`Reaction element for action '${action}' not found with selector '${reactionSelector}'.`);
  }

  // Always close the panel afterwards for a consistent experience.
  // The panel might close automatically, but this ensures it.
  setTimeout(() => {
    if (reactionsToggleButton.getAttribute('aria-pressed') === 'true') {
      reactionsToggleButton.click();
    }
  }, 500); // Delay to allow the reaction animation to be seen
}

/**
 * Handles incoming commands from the background script.
 */
function handleCommand(message) {
  // The background script validates all incoming commands from the native host,
  // so we can trust messages received from it.
  if (!message || !message.action) {
    return;
  }
  const action = message.action;

  console.log("Received command:", action);
  const selector = SELECTORS[action];

  if (action.startsWith('send_reaction_')) {
    handleReactionCommand(action, selector);
  } else if (selector) {
    const element = document.querySelector(selector);
    if (element) {
      console.log(`Clicking element for action: ${action}`);
      element.click();
    } else {
      console.warn(`Element for action '${action}' not found with selector '${selector}'.`);
    }
  } else {
    console.warn(`No selector defined for action: ${action}`);
  }
}

/**
 * Uses a MutationObserver to watch for changes in the Meet UI and sync state.
 */
function setupStateObserver() {
  const observer = new MutationObserver((mutationsList) => {
    // Check for the start or end of a call, which is the most significant state change.
    const micButton = document.querySelector(SELECTORS.toggle_mute);

    if (micButton && !inCall) {
      // --- Call has just started ---
      console.log("Call has started. Syncing initial state.");
      inCall = true;
      // Sync all controls now that we've joined.
      const camButton = document.querySelector(SELECTORS.toggle_camera);
      const handButton = document.querySelector(SELECTORS.raise_hand);
      sendStatus('microphone', micButton.getAttribute('data-is-muted') === 'false');
      // Also check panel states on join
      const chatPanelButton = document.querySelector(SELECTORS.toggle_chat_panel);
      const participantsPanelButton = document.querySelector(SELECTORS.toggle_participants_panel);

      if (camButton) sendStatus('camera', camButton.getAttribute('data-is-muted') === 'false');
      if (handButton) sendStatus('hand', handButton.getAttribute('aria-pressed') === 'true');

      // Sync initial presentation state
      const isPresenting = !!document.querySelector('[aria-label*="Stop presenting" i]');
      lastKnownPresentingState = isPresenting;
      sendStatus('presenting', isPresenting);
      if (chatPanelButton) sendStatus('chat_panel', chatPanelButton.getAttribute('aria-pressed') === 'true');
      if (participantsPanelButton) sendStatus('participants_panel', participantsPanelButton.getAttribute('aria-pressed') === 'true');
    } else if (!micButton && inCall) {
      // --- Call has just ended ---
      console.log("Call has ended.");
      inCall = false;
      sendStatus('call', false); // Notify plugin that the call ended.
      // Ensure we reset the presenting state if it was active
      if (lastKnownPresentingState) {
        lastKnownPresentingState = false;
        sendStatus('presenting', false);
      }
      return; // No other states to check, UI is gone.
    }

    if (!inCall) {
      return; // Don't process other mutations if not in a call
    }

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
        } else if (ariaLabel.toLowerCase().includes('chat with everyone')) {
          sendStatus('chat_panel', isPressed);
        } else if (ariaLabel.toLowerCase().includes('show everyone')) {
          sendStatus('participants_panel', isPressed);
        }
      }
    }

    // Check for presentation state change on any DOM mutation. This is more reliable
    // than trying to catch the specific attribute/node change for this button.
    const isPresentingNow = !!document.querySelector('[aria-label*="Stop presenting" i]');
    if (isPresentingNow !== lastKnownPresentingState) {
      console.log(`Presenting state changed to: ${isPresentingNow}`);
      lastKnownPresentingState = isPresentingNow;
      sendStatus('presenting', isPresentingNow);
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-is-muted', 'aria-pressed'],
    subtree: true,
    childList: true, // Watch for elements being added/removed from the DOM
  });
  console.log("Meet Controller: State observer is now active.");
}

// Listen for messages (commands) from the background script.
chrome.runtime.onMessage.addListener(handleCommand);

// Start observing the page for state changes.
setupStateObserver();
