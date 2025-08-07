import json
import logging
import os
import socket
import struct
import sys
import threading
from typing import Any

from pydantic import ValidationError

from models import ActionCommand, StatusUpdate
from native_messaging_handler import NativeMessagingHandler

# --- Configuration ---
XDG_RUNTIME_DIR = os.getenv("XDG_RUNTIME_DIR", "/tmp")
SOCKET_PATH = os.path.join(
  XDG_RUNTIME_DIR, "app/com.core477.StreamController/meet_plugin.sock"
)

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
  try:
    # Validate that the message from Chrome is a valid StatusUpdate
    status = StatusUpdate.model_validate(message_from_chrome)
    message_to_send = status.model_dump()
  except ValidationError as e:
    logger.error(f"Invalid message from Chrome, not forwarding: {e}")
    return

  if sc_socket:
    try:
      encoded_message = json.dumps(message_to_send).encode("utf-8")
      length_prefix = struct.pack("@I", len(encoded_message))
      sc_socket.sendall(length_prefix)
      sc_socket.sendall(encoded_message)
      logger.info(f"Sent to SC: {message_to_send}")
    except (ConnectionResetError, BrokenPipeError):
      logger.error("Connection to StreamController lost.")
      sys.exit(1)


chrome_handler = NativeMessagingHandler(send_to_streamcontroller)


def listen_to_streamcontroller() -> None:
  """Listens on the socket for messages from the main app and forwards them to Chrome."""

  assert sc_socket is not None, "StreamController socket not initialized."

  while True:
    try:
      raw_length = sc_socket.recv(4)
      if not raw_length:
        break
      message_length = struct.unpack("@I", raw_length)[0]
      message_content = sc_socket.recv(message_length).decode("utf-8")
      message = json.loads(message_content)

      # Validate that the message from the plugin is a valid ActionCommand
      try:
        command = ActionCommand.model_validate(message)
        message_to_send = command.model_dump()
      except ValidationError as e:
        logger.error(
          f"Invalid command from plugin, not forwarding to Chrome: {e}"
        )
        continue
      chrome_handler.send_message(message_to_send)
      logger.info(f"Received from SC: {message_to_send}")
    except (ConnectionResetError, BrokenPipeError, OSError):
      logger.info("StreamController closed the connection. Exiting.")
      sys.exit(0)


if __name__ == "__main__":
  logger.info("Meet Proxy started by Chrome.")
  try:
    sc_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sc_socket.connect(SOCKET_PATH)
  except (ConnectionRefusedError, FileNotFoundError):
    logger.error(
      f"Connection to StreamController at {SOCKET_PATH} refused or not found."
    )
    sys.exit(1)

  sc_listener_thread = threading.Thread(
    target=listen_to_streamcontroller, daemon=True
  )
  sc_listener_thread.start()

  chrome_handler.listen()
  logger.info("Chrome connection closed. Proxy shutting down.")
