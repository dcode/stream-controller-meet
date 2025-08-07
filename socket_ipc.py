import json
import logging
import socket
import struct
import threading
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class SocketIPCServer:
    """A simple socket server to communicate with a single client (the proxy)."""

    def __init__(
        self,
        host: str,
        port: int,
        message_callback: Callable[[dict[str, Any]], None],
    ):
        self.host = host
        self.port = port
        self.message_callback = message_callback
        self.client_socket: socket.socket | None = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def listen(self) -> None:
        """Listens for a single client connection and handles messages."""
        self.server_socket.listen(1)
        logger.info(f"SocketIPCServer listening on {self.host}:{self.port}")
        # This will block until the proxy connects.
        self.client_socket, addr = self.server_socket.accept()
        logger.info(f"SocketIPCServer accepted connection from {addr}")
        self._handle_client()

    def _handle_client(self) -> None:
        """Reads messages from the connected client in a loop."""
        while self.client_socket:
            try:
                raw_length = self.client_socket.recv(4)
                if not raw_length:
                    break

                message_length = struct.unpack("@I", raw_length)[0]
                message_content = self.client_socket.recv(message_length).decode("utf-8")
                message = json.loads(message_content)
                self.message_callback(message)
            except (ConnectionResetError, BrokenPipeError):
                logger.warning("Socket connection with proxy lost.")
                break
            except Exception:
                logger.exception("Error handling message from socket client.")
                break
        self.client_socket = None
        logger.info("Client disconnected. Ready for new connection.")
        # Optional: loop back to self.listen() if you want to accept new connections
        # without restarting the whole plugin. For simplicity, we stop here.

    def send_message(self, message: dict[str, Any]) -> None:
        """Sends a message to the connected client."""
        if not self.client_socket:
            return

        try:
            encoded_message = json.dumps(message).encode("utf-8")
            length_prefix = struct.pack("@I", len(encoded_message))
            self.client_socket.sendall(length_prefix)
            self.client_socket.sendall(encoded_message)
        except (ConnectionResetError, BrokenPipeError):
            logger.warning("Could not send message, socket connection lost.")
            self.client_socket = None
