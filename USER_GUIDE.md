# Google Meet Controller User Guide

This guide will walk you through the process of installing and using the Google Meet Controller plugin for StreamController.

## Installation

### 1. Install the Plugin

To install the plugin, run the following command in your terminal:

```bash
python __install__.py
```

This will install the native messaging host, which is required for the plugin to communicate with the Chrome extension.

### 2. Install the Chrome Extension

1.  Open Chrome and navigate to `chrome://extensions`.
2.  Enable "Developer mode" in the top right corner.
3.  Click "Load unpacked" and select the `contrib/chrome-extension/dist` directory.

## Usage

Once the plugin and the Chrome extension are installed, you can start using the plugin in the StreamController app.

1.  Open the StreamController app.
2.  Drag and drop the Google Meet actions onto the StreamController grid.
3.  Join a Google Meet call.

The icons on the StreamController will update to reflect the state of the call. You can press the buttons to toggle the mute, camera, and other features.

## Troubleshooting

If you encounter any issues, please check the following:

*   Make sure the native messaging host is installed correctly. You can check the `com.github.dcode.stream_controller_meet.json` file in your Chrome config directory.
*   Make sure the Chrome extension is installed and enabled.
*   Check the Chrome extension's console for any error messages.
