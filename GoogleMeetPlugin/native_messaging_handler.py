import json
import logging
import struct
import sys
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class NativeMessagingHandler:
  """Handles the native messaging protocol to communicate with a browser extension."""

  def __init__(self, message_callback: Callable[[dict[str, Any]], None]):
    """
    Initializes the NativeMessagingHandler.

    Args:
        message_callback: A function to call when a message is received.
    """
    self.message_callback = message_callback

  def listen(self) -> None:
    """Listens for messages from the Chrome extension via stdin.

    This method runs in a loop, reading messages until stdin is closed.
    """
    logger.info("Native messaging handler started listening.")
    while True:
      try:
        # Read the 4-byte length prefix
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
          logger.info("Stdin closed, exiting listener loop.")
          break

        message_length = struct.unpack("@I", raw_length)[0]

        # Read the message content
        message_content = sys.stdin.buffer.read(message_length).decode("utf-8")
        message = json.loads(message_content)

        logger.debug("Received message: %s", message)
        self.message_callback(message)

      except (struct.error, json.JSONDecodeError) as e:
        logger.error("Error decoding message: %s", e)
        continue
      except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("An unexpected error occurred in listener.")
        break

  def send_message(self, message: dict[str, Any]) -> None:
    """Sends a message to the Chrome extension via stdout.

    Args:
        message: A JSON-serializable dictionary to send.
    """
    try:
      encoded_message = json.dumps(message).encode("utf-8")
      length_prefix = struct.pack("@I", len(encoded_message))

      sys.stdout.buffer.write(length_prefix)
      sys.stdout.buffer.write(encoded_message)
      sys.stdout.buffer.flush()
      logger.debug("Sent message: %s", message)
    except Exception:  # pylint: disable=broad-exception-caught
      logger.exception("Error sending message.")
