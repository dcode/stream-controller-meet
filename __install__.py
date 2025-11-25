"""Installer script for the Google Meet StreamController plugin."""

import json
import os
import platform
import shutil
import sys
from pathlib import Path


def get_chrome_config_path() -> Path:
    """Get the path to the Chrome config directory."""
    if platform.system() == "Linux":
        return Path.home() / ".config" / "google-chrome"
    elif platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    elif platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")


def install():
    """Install the plugin and the Chrome extension."""
    # Get the path to the native messaging manifest file
    chrome_config_path = get_chrome_config_path()
    native_messaging_path = chrome_config_path / "NativeMessagingHosts"
    native_messaging_path.mkdir(parents=True, exist_ok=True)
    manifest_path = native_messaging_path / "com.github.dcode.stream_controller_meet.json"

    # Get the path to the proxy script
    proxy_script_path = Path(__file__).parent / "GoogleMeetPlugin" / "meet_proxy.py"

    # Create the native messaging manifest
    manifest = {
        "name": "com.github.dcode.stream_controller_meet",
        "description": "Proxy for Google Meet StreamController plugin",
        "path": str(proxy_script_path),
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://knibfceijpblncljdnjjb-dhgdnleflk/",
        ],
    }

    # Write the manifest to the file
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Native messaging manifest created at {manifest_path}")

    # Install the Chrome extension
    # This part is a bit tricky, as we can't programmatically install a Chrome
    # extension. We'll provide instructions to the user instead.
    print("\nTo install the Chrome extension, follow these steps:")
    print("1. Open Chrome and navigate to chrome://extensions")
    print("2. Enable 'Developer mode' in the top right corner")
    print("3. Click 'Load unpacked' and select the 'contrib/chrome-extension' directory")
    print(f"   (located at {Path(__file__).parent / 'contrib' / 'chrome-extension'})")


if __name__ == "__main__":
    install()
