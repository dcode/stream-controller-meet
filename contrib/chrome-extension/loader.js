/**
 * This script acts as a loader for the main content script module.
 * This is the standard pattern for using ES modules in content scripts for MV3.
 */
(async () => {
  const src = chrome.runtime.getURL('content_script.mjs');
  await import(src);
})();