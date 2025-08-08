export const SELECTORS = {
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

export function sendStatus(control, is_on) {
  const statusMessage = {
    status: 'update',
    control: control,
    state: is_on ? 'on' : 'off'
  };
  console.log("Sending status:", statusMessage);
  chrome.runtime.sendMessage(statusMessage);
}

export async function handleReactionCommand(action, reactionSelector) {
  const reactionsToggleButton = document.querySelector(SELECTORS.toggle_reactions);
  if (!reactionsToggleButton) {
    console.warn("Could not find the main 'Send a reaction' button.");
    return;
  }

  const wasPanelOpen = reactionsToggleButton.getAttribute('aria-pressed') === 'true';

  if (!wasPanelOpen) {
    reactionsToggleButton.click();
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  const reactionElement = document.querySelector(reactionSelector);
  if (reactionElement) {
    console.log(`Clicking reaction element for action: ${action}`);
    reactionElement.click();
  } else {
    console.warn(`Reaction element for action '${action}' not found with selector '${reactionSelector}'.`);
  }

  setTimeout(() => {
    if (reactionsToggleButton.getAttribute('aria-pressed') === 'true') {
      reactionsToggleButton.click();
    }
  }, 500);
}

export function handleCommand(message) {
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

export function setupStateObserver() {
  let lastKnownPresentingState = false;
  let inCall = false;

  const observer = new MutationObserver((mutationsList) => {
    const micButton = document.querySelector(SELECTORS.toggle_mute);

    if (micButton && !inCall) {
      console.log("Call has started. Syncing initial state.");
      inCall = true;
      const camButton = document.querySelector(SELECTORS.toggle_camera);
      const handButton = document.querySelector(SELECTORS.raise_hand);
      sendStatus('microphone', micButton.getAttribute('data-is-muted') === 'false');
      const chatPanelButton = document.querySelector(SELECTORS.toggle_chat_panel);
      const participantsPanelButton = document.querySelector(SELECTORS.toggle_participants_panel);

      if (camButton) sendStatus('camera', camButton.getAttribute('data-is-muted') === 'false');
      if (handButton) sendStatus('hand', handButton.getAttribute('aria-pressed') === 'true');

      const isPresenting = !!document.querySelector('[aria-label*="Stop presenting" i]');
      lastKnownPresentingState = isPresenting;
      sendStatus('presenting', isPresenting);
      if (chatPanelButton) sendStatus('chat_panel', chatPanelButton.getAttribute('aria-pressed') === 'true');
      if (participantsPanelButton) sendStatus('participants_panel', participantsPanelButton.getAttribute('aria-pressed') === 'true');
    } else if (!micButton && inCall) {
      console.log("Call has ended.");
      inCall = false;
      sendStatus('call', false);
      if (lastKnownPresentingState) {
        lastKnownPresentingState = false;
        sendStatus('presenting', false);
      }
      return;
    }

    if (!inCall) {
      return;
    }

    for (const mutation of mutationsList) {
      if (mutation.type === 'attributes' && mutation.target.hasAttribute('data-is-muted')) {
        const element = mutation.target;
        const isMuted = element.getAttribute('data-is-muted') === 'true';

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
    childList: true,
  });
  console.log("Meet Controller: State observer is now active.");
}

function main() {
    console.log("Meet Controller: Content script injected and running.");
    chrome.runtime.onMessage.addListener(handleCommand);
    setupStateObserver();
}

if (typeof window !== 'undefined' && window.chrome) {
  main();
}