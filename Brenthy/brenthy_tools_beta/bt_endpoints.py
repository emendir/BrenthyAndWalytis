"""The websocket-level communication machinery for BrenthyAPI.

This file contains all the websocket-level communication machinery
`brenthy_api` needs to communicate with Brenthy via all BrenthyAPI protocols.
More specifically, it contains different functions and classes for publishing
events and receiving & replying to requests via ZMQ & TCP sockets
This file has a counterpart under ../brenthy_tools_beta/bt_endpoints.py.
'bt' in bt_endpoints tands for Brenthy Tools, to distinguish this
file's name from bt_endpoints.py, where 'bat' stands for Brenthy API Terminal.
"""

import socket
import time
from abc import ABC, abstractmethod
from types import FunctionType

from brenthy_tools_beta import log
from brenthy_tools_beta.utils import from_b255_no_0s, to_b255_no_0s

try:
    # load ZMQ
    import zmq

    ZMQ_CONTEXT: zmq.sugar.context.Context | None = zmq.Context()
except:  # pylint:disable=bare-except
    log.error("Failed to set up ZMQ communications. Using TCP only.")
    ZMQ_CONTEXT = None

BUFFER_SIZE = 4096  # the TCP buffer size for processing reveived data
REQUEST_TIMEOUT_S = 180
CONNECT_TIMEOUT_S = 2


def send_request_zmq(
    request: bytearray | bytes,
    socket_address: tuple[str, int],
    timeout: int = REQUEST_TIMEOUT_S,
) -> bytes:
    """Send a request to the given address, expecting a reply.

    Args:
        request (bytearray): the data to send
        socket_address (tuple[str,int]): IP address and port number to send to
        timeout (int): how long to wait before giving up
    Returns:
        bytearray: reply received from the endpoint after sending the request
    """
    if not ZMQ_CONTEXT:
        raise CantConnectToSocketError(protocol="ZMQ") from None

    zmq_socket = ZMQ_CONTEXT.socket(zmq.REQ)
    zmq_socket.setsockopt(zmq.LINGER, 1)

    zmq_socket.connect(
        f"tcp://{socket_address[0]}:{socket_address[1]}",
        # timeout=CONNECT_TIMEOUT_S*1000
    )

    zmq_socket.send(request)
    zmq_socket.poll(timeout=timeout * 1000, flags=zmq.PollEvent.POLLIN)
    try:
        reply = zmq_socket.recv(flags=zmq.NOBLOCK)
    except zmq.error.Again:
        raise CantConnectToSocketError(
            protocol="ZMQ", address=socket_address
        ) from None
    zmq_socket.close()
    return reply


def send_request_tcp(
    request: bytearray | bytes, socket_address: tuple[str, int]
) -> bytes:
    """Send a request to the given address, expecting a reply.

    Args:
        request (bytearray): the data to send
        socket_address (tuple[str,int]): IP address and port number to send to
    Returns:
        bytearray: reply received from the endpoint after sending the request
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((socket_address[0], socket_address[1]))
        except ConnectionRefusedError:
            raise CantConnectToSocketError(
                protocol="TCP", address=socket_address
            ) from None
        _tcp_send_counted(s, request)
        reply = _tcp_recv_counted(s)
        return reply


class CantConnectToSocketError(Exception):
    """Error for TCP or ZMQ failures to connect to api_terminal sockets."""

    def_message = "Failed to connect to socket"
    address = None  # IP address & port
    protocol = ""  # TCP or ZMQ

    def __init__(
        self,
        message: str = def_message,
        protocol: str = "",
        address: tuple[str, int] | None = None,
    ):
        """Create a CantConnectToSocketError exception.

        Args:
            message (str): a message to store in this Exception
            protocol (str): the protocol (ZMQ, TCP) the failed connection used
            address (str): target websocket address of the failed connection
        """
        self.message = message
        if protocol.upper() in ["ZMQ", "TCP"]:
            self.protocol = protocol.upper()
        if address:
            self.address = address

    def __str__(self) -> str:
        """Get a string representing this Exception."""
        error_message = ""
        if self.protocol:
            error_message += f"{self.protocol}: "
        if self.address:
            error_message += f"{self.address}: "
        error_message += self.message
        return error_message


def _tcp_send_counted(sock: socket.socket, data: bytearray | bytes) -> None:
    length = len(data)
    sock.send(to_b255_no_0s(length) + bytearray([0]))
    sock.send(data)


def _tcp_recv_counted(sock: socket.socket, timeout: int = 5) -> bytes:
    # make socket non blocking
    sock.setblocking(False)

    # total data partwise in an array
    total_data = bytes()
    data = bytes()
    length = 0
    # beginning time
    begin = time.time()
    while True:
        # if you got some data, then break after timeout
        if len(total_data) > 0 and time.time() - begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        if time.time() - begin > timeout * 2:
            break

        # recv something
        try:
            data = sock.recv(BUFFER_SIZE)
            if data:
                if not length:
                    if data.index(0):
                        total_data += data[: data.index(0)]
                        length = from_b255_no_0s(total_data)
                        total_data = data[data.index(0) + 1:]
                    else:
                        total_data += data
                else:
                    total_data += data

                if length:
                    if len(total_data) == length:
                        return total_data
                    if len(total_data) > length:
                        raise OverflowError("Received more data than expected!")
                    # change the beginning time for measurement
                    begin = time.time()
        except:  # pylint:disable=bare-except
            pass
    return total_data


class EventListener(ABC):
    """Abstract class for EventListener, which all BAP modules implement."""

    def __init__(
        self,
        eventhandler: FunctionType,
        topics: (list[str] | str | None) = None,
    ):
        """Create an EventListener."""
        pass

    @abstractmethod
    def terminate(self) -> None:
        """Stop listening for events and clean up resources."""
        pass
