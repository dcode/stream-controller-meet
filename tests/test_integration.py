"""Integration tests for the plugin."""

import json
import os
import socket
import struct
import threading
import time
from unittest.mock import MagicMock

import pytest

from GoogleMeetPlugin.socket_ipc import SocketIPCServer


def test_socket_ipc_communication():
    """Test that the SocketIPCServer can send and receive messages."""
    socket_path = "/tmp/test_socket.sock"
    message_callback = MagicMock()

    # Start the server in a separate thread
    server = SocketIPCServer(socket_path, message_callback)
    server_thread = threading.Thread(target=server.listen)
    server_thread.daemon = True
    server_thread.start()

    # Wait for the server to start listening
    time.sleep(0.1)

    # Create a client and connect to the server
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client_socket.connect(socket_path)

    # Send a message from the client to the server
    message_to_server = {"status": "update", "control": "camera", "state": "on"}
    encoded_message = json.dumps(message_to_server).encode("utf-8")
    length_prefix = struct.pack("@I", len(encoded_message))
    client_socket.sendall(length_prefix)
    client_socket.sendall(encoded_message)

    # Wait for the server to process the message
    time.sleep(0.1)

    # Check that the server's callback was called with the correct message
    message_callback.assert_called_once_with(message_to_server)

    # Send a message from the server to the client
    message_to_client = {"action": "toggle_mute"}
    server.send_message(message_to_client)

    # Wait for the client to receive the message
    time.sleep(0.1)

    # Read the message from the client socket
    raw_length = client_socket.recv(4)
    message_length = struct.unpack("@I", raw_length)[0]
    message_content = client_socket.recv(message_length).decode("utf-8")
    received_message = json.loads(message_content)

    # Check that the client received the correct message
    assert received_message == message_to_client

    # Clean up
    client_socket.close()
    server.server_socket.close()
    if os.path.exists(socket_path):
        os.unlink(socket_path)
