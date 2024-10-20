# Copyright (c) Aymeric Augustin and contributors
# see https://github.com/python-websockets/websockets/blob/main/LICENSE

import logging
import socket
import threading
import uuid
from typing import Optional, Dict

from websockets.sync.client import ClientProtocol, connect as _connect
from websockets.sync.connection import Connection
from websockets.sync.messages import Assembler
from websockets.sync.utils import Deadline
from websockets.datastructures import HeadersLike
from websockets.protocol import Protocol
from websockets.http import USER_AGENT
from websockets.http11 import Request, Response
from websockets.protocol import CONNECTING, OPEN, Event
from websockets.typing import LoggerLike


class DaemonConnection(Connection):
    """
    Threaded implementation of a WebSocket connection.

    :class:`Connection` provides APIs shared between WebSocket servers and
    clients.

    You shouldn't use it directly. Instead, use
    :class:`~websockets.sync.client.ClientConnection` or
    :class:`~websockets.sync.server.ServerConnection`.

    """

    recv_bufsize = 65536

    def __init__(
        self,
        socket: socket.socket,
        protocol: Protocol,
        *,
        close_timeout: Optional[float] = 10,
    ) -> None:
        self.socket = socket
        self.protocol = protocol
        self.close_timeout = close_timeout

        # Inject reference to this instance in the protocol's logger.
        self.protocol.logger = logging.LoggerAdapter(
            self.protocol.logger,
            {"websocket": self},
        )

        # Copy attributes from the protocol for convenience.
        self.id: uuid.UUID = self.protocol.id
        """Unique identifier of the connection. Useful in logs."""
        self.logger: LoggerLike = self.protocol.logger
        """Logger for this connection."""
        self.debug = self.protocol.debug

        # HTTP handshake request and response.
        self.request: Optional[Request] = None
        """Opening handshake request."""
        self.response: Optional[Response] = None
        """Opening handshake response."""

        # Mutex serializing interactions with the protocol.
        self.protocol_mutex = threading.Lock()

        # Assembler turning frames into messages and serializing reads.
        self.recv_messages = Assembler()

        # Whether we are busy sending a fragmented message.
        self.send_in_progress = False

        # Deadline for the closing handshake.
        self.close_deadline: Optional[Deadline] = None

        # Mapping of ping IDs to pong waiters, in chronological order.
        self.pings: Dict[bytes, threading.Event] = {}

        # Receiving events from the socket.

        # !!! Start patch based on 12.0 (this is the only patched line) !!!
        # self.recv_events_thread = threading.Thread(target=self.recv_events)
        self.recv_events_thread = threading.Thread(target=self.recv_events, daemon=True)
        # !!! End patch !!!

        self.recv_events_thread.start()

        # Exception raised in recv_events, to be chained to ConnectionClosed
        # in the user thread in order to show why the TCP connection dropped.
        self.recv_events_exc: Optional[BaseException] = None


class DaemonClientConnection(DaemonConnection):
    """
    Threaded implementation of a WebSocket client connection.

    :class:`ClientConnection` provides :meth:`recv` and :meth:`send` methods for
    receiving and sending messages.

    It supports iteration to receive messages::

        for message in websocket:
            process(message)

    The iterator exits normally when the connection is closed with close code
    1000 (OK) or 1001 (going away) or without a close code. It raises a
    :exc:`~websockets.exceptions.ConnectionClosedError` when the connection is
    closed with any other code.

    Args:
        socket: Socket connected to a WebSocket server.
        protocol: Sans-I/O connection.
        close_timeout: Timeout for closing the connection in seconds.

    """

    def __init__(
        self,
        socket: socket.socket,
        protocol: ClientProtocol,
        *,
        close_timeout: Optional[float] = 10,
    ) -> None:
        self.protocol: ClientProtocol
        self.response_rcvd = threading.Event()
        super().__init__(
            socket,
            protocol,
            close_timeout=close_timeout,
        )

    def handshake(
        self,
        additional_headers: Optional[HeadersLike] = None,
        user_agent_header: Optional[str] = USER_AGENT,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Perform the opening handshake.

        """
        with self.send_context(expected_state=CONNECTING):
            self.request = self.protocol.connect()
            if additional_headers is not None:
                self.request.headers.update(additional_headers)
            if user_agent_header is not None:
                self.request.headers["User-Agent"] = user_agent_header
            self.protocol.send_request(self.request)

        if not self.response_rcvd.wait(timeout):
            self.close_socket()
            self.recv_events_thread.join()
            raise TimeoutError("timed out during handshake")

        if self.response is None:
            self.close_socket()
            self.recv_events_thread.join()
            raise ConnectionError("connection closed during handshake")

        if self.protocol.state is not OPEN:
            self.recv_events_thread.join(self.close_timeout)
            self.close_socket()
            self.recv_events_thread.join()

        if self.protocol.handshake_exc is not None:
            raise self.protocol.handshake_exc

    def process_event(self, event: Event) -> None:
        """
        Process one incoming event.

        """
        # First event - handshake response.
        if self.response is None:
            assert isinstance(event, Response)
            self.response = event
            self.response_rcvd.set()
        # Later events - frames.
        else:
            super().process_event(event)

    def recv_events(self) -> None:
        """
        Read incoming data from the socket and process events.

        """
        try:
            super().recv_events()
        finally:
            # If the connection is closed during the handshake, unblock it.
            self.response_rcvd.set()


# Simple shim
def connect(url):
    return _connect(url, create_connection=DaemonClientConnection)
