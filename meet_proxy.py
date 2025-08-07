import json
import logging
import socket
import struct
import sys
import threading
from typing import Any

from native_messaging_handler import NativeMessagingHandler

# --- Configuration ---
HOST = "127.0.0.1"
PORT = 35677  # Choose a unique port for this plugin
LOG_FILE = "/tmp/streamcontroller-meet-proxy.log"

# --- Logging Setup ---
# Native Messaging uses stdout, so we must log to a file for debugging.
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Globals ---
sc_socket: socket.socket | None = None


def send_to_streamcontroller(message_from_chrome: dict[str, Any]) -> None:
    """Callback for NativeMessagingHandler. Forwards message to the main app via socket."""
    if sc_socket:
        try:
            encoded_message = json.dumps(message_from_chrome).encode("utf-8")
            length_prefix = struct.pack("@I", len(encoded_message))
            sc_socket.sendall(length_prefix)
            sc_socket.sendall(encoded_message)
            logger.info(f"Sent to SC: {message_from_chrome}")
        except (ConnectionResetError, BrokenPipeError):
            logger.error("Connection to StreamController lost.")
            sys.exit(1)


chrome_handler = NativeMessagingHandler(send_to_streamcontroller)


def listen_to_streamcontroller() -> None:
    """Listens on the socket for messages from the main app and forwards them to Chrome."""
    while True:
        try:
            raw_length = sc_socket.recv(4)
            if not raw_length:
                break
            message_length = struct.unpack("@I", raw_length)[0]
            message_content = sc_socket.recv(message_length).decode("utf-8")
            message = json.loads(message_content)
            chrome_handler.send_message(message)
            logger.info(f"Received from SC: {message}")
        except (ConnectionResetError, BrokenPipeError, OSError):
            logger.info("StreamController closed the connection. Exiting.")
            sys.exit(0)


if __name__ == "__main__":
    logger.info("Meet Proxy started by Chrome.")
    try:
        sc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        logger.error(f"Connection to StreamController at {HOST}:{PORT} refused.")
        sys.exit(1)

    sc_listener_thread = threading.Thread(target=listen_to_streamcontroller, daemon=True)
    sc_listener_thread.start()

    chrome_handler.listen()
    logger.info("Chrome connection closed. Proxy shutting down.")
