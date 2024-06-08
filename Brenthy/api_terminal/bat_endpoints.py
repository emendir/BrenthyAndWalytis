"""Websocket-level communication machinery for BrenthyAPI protocol modules.

This file contains the websocket-level communication machinery common to
multiple BrenthyAPI protocols on Brenthy Core's side of the communication.
"""

import json
import socket
import time
from threading import Thread
from typing import Callable

import zmq
from brenthy_tools_beta import log
from brenthy_tools_beta.utils import from_b255_no_0s, to_b255_no_0s

BUFFER_SIZE = 4096  # the communication buffer size

TERMINATTION_CODE = b"close"


class ZmqMultiRequestsReceiver:
    """Listen for RPC requests and respond with replies via ZMQ."""

    def __init__(
        self,
        socket_address: tuple[str, int],
        handle_request: Callable[[bytes], bytes],
    ):
        """Listen to incoming RPC requests using the ZMQ protocol."""
        self.zmq_context = zmq.Context()
        self.socket_address = socket_address
        self.handle_request = handle_request
        self._terminate = False
        self.listener_thread = Thread(target=self._listen, args=())
        self.listener_thread.start()

    def _listen(self) -> None:
        try:
            log.debug("ZMQ creating socket...")

            self.zmq_socket = self.zmq_context.socket(zmq.ROUTER)
            self.zmq_socket.setsockopt(zmq.LINGER, 1)
            self.zmq_socket.bind(
                f"tcp://{self.socket_address[0]}:{self.socket_address[1]}"
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.error(str(error))
            return

        try:
            while True:
                # Accept incoming connections
                log.debug("ZMQ waiting for request...")

                identity, _, request = self.zmq_socket.recv_multipart()
                log.debug("ZMQ processing request...")

                if request == TERMINATTION_CODE:
                    log.debug("ZMQ closing socket...")

                    self.zmq_socket.close()
                    return
                # Spawn a new thread to handle each connection
                Thread(
                    target=self.handle_zmq_connection,
                    args=(identity, request),
                    daemon=True,
                ).start()
        finally:
            log.debug("ZMQ closing socket...")
            self.zmq_socket.close()

    def handle_zmq_connection(self, identity: bytes, request: bytes) -> None:
        """Handle a freshly accepted ZeroMQ connection."""
        # Process the request
        log.debug("ZMQ handling new connection...")
        reply = self.handle_request(request)

        log.debug("ZMQ sending reply...")

        # Send the reply back to the client
        self.zmq_socket.send_multipart([identity, b"", reply])

    def terminate(self) -> None:
        """Stop listening for requests and clean up resources."""
        try:
            log.debug("ZMQ shutting down socket...")
            if not self.listener_thread.is_alive():
                log.debug("ZMQ socket must already be shut down.")

                return
            self._terminate = True
            sock = self.zmq_context.socket(zmq.REQ)
            self.zmq_socket.setsockopt(zmq.LINGER, 1)

            sock.connect(
                f"tcp://{self.socket_address[0]}:{self.socket_address[1]}"
            )
            sock.send("close".encode())
            sock.close()
            self.listener_thread.join()
        except Exception as error:
            log.error(
                "error in API-Terminal.ZMQ-ZmqRequestsReceiver.terminate(): "
                f"{error}"
            )
        log.debug("ZMQ: terminating context.")
        # self.zmq_context.term()

    def __del__(self):
        """Stop listening for requests and clean up resources."""
        self.terminate()


class TcpMultiRequestsReceiver:
    """Listen for RPC requests and respond with replies via plain TCP."""

    def __init__(
        self,
        socket_address: tuple[str, int],
        handle_request: Callable[[bytes], bytes],
    ):
        """Listen to incoming RPC requests using the ZMQ protocol."""
        self.socket_address = socket_address
        self.handle_request = handle_request
        self._terminate = False
        self.listener_thread = Thread(target=self._listen, args=())
        self.listener_thread.start()

    def _listen(self) -> None:
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.bind((self.socket_address[0], self.socket_address[1]))
            tcp_socket.listen()
            while not self._terminate:
                conn, addr = tcp_socket.accept()
                Thread(
                    target=self.handle_tcp_connection,
                    args=(conn, addr),
                    name="API-Terminal.handle_tcp_connection",
                ).start()
            tcp_socket.close()
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.error(str(error))

    def handle_tcp_connection(
        self, conn: socket.socket, addr: tuple[str, int]
    ) -> None:
        """Handle a freshly accepted TCP connection."""
        request = _tcp_recv_counted(conn)
        if request == bytearray(TERMINATTION_CODE):
            conn.close()
            return
        if request:
            reply = self.handle_request(request)
            _tcp_send_counted(conn, reply)
        else:
            log.warning("API-Terminal.TCP-Listener: Received null data")
            conn.close()

    def terminate(self) -> None:
        """Stop listening for requests and clean up resources."""
        try:
            if not self.listener_thread.is_alive():
                return
            self._terminate = True
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.socket_address)
            _tcp_send_counted(sock, "close".encode())

            sock.close()
            self.listener_thread.join()
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.error(
                "error in API-Terminal.ZMQ-ZmqRequestsReceiver.terminate(): "
                f"{error}"
            )

    def __del__(self):
        """Stop listening for requests and clean up resources."""
        self.terminate()


class ZmqPublisher:
    """Class for publishing data on a Publish-Subscribe socket."""

    def __init__(self, address: tuple[str, int]):
        """Create an object for publishing data on a pubsub socket."""
        self._terminated = False
        self.zmq_context = zmq.Context()
        self.address = address
        self.pub_socket = self.zmq_context.socket(zmq.PUB)
        self.pub_socket.setsockopt(zmq.LINGER, 1)

        # Binds the socket to a predefined port on localhost
        self.pub_socket.bind(f"tcp://{self.address[0]}:{self.address[1]}")

    def publish(self, data: dict) -> None:
        """Publish data on a Publish-Subscribe socket."""
        if self._terminated:
            log.error(
                "Can't publish message as this ZmqPublisher has been "
                "terminated."
            )
            return
        self.pub_socket.send_string(json.dumps(data))

    def terminate(self) -> None:
        """Clean up resources."""
        if not self._terminated:
            log.debug("Shutting down ZMQ resources.")
            self.pub_socket.close()
            # self.zmq_context.term()
            self._terminated = True

    def __del__(self):
        """Clean up resources."""
        self.terminate()


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
        elif time.time() - begin > timeout * 2:
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
        except:
            pass
    return total_data


def _tcp_send_counted(sock: socket.socket, data: bytearray | bytes) -> None:
    length = len(data)
    sock.send(to_b255_no_0s(length) + bytearray([0]))
    sock.send(data)
