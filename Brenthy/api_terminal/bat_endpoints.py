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
from time import sleep
BUFFER_SIZE = 4096  # the communication buffer size

TERMINATTION_CODE = b"close"

# keep track of contexts to avoid problems caused by garbage collector
CONTEXTS = []


class ZmqMultiRequestsReceiver:
    """Listen for RPC requests and respond with replies via ZMQ."""

    def __init__(
        self,
        socket_address: tuple[str, int],
        handle_request: Callable[[bytes], bytes],
        max_parallel_handlers: int = 20
    ):
        """Listen to incoming RPC requests using the ZMQ protocol."""
        self.zmq_context = zmq.Context()
        CONTEXTS.append(self.zmq_context)
        self.socket_address = socket_address
        self.handle_request = handle_request
        self.max_parallel_handlers = max_parallel_handlers
        self._terminate = False
        self.dealer_socket: None | zmq.Socket = None
        self.router_socket: None | zmq.Socket = None
        self.listener_thread = Thread(
            target=self._listen, args=(),
            name="ZmqMultiRequestsReceiver-listener"
        )
        self.listener_thread.start()
        self.workers: list[Thread] = []
        self._start_workers()

    def _start_workers(self) -> None:
        """Start worker threads which will handle requests."""
        for i in range(self.max_parallel_handlers):
            worker = Thread(
                target=self._worker_routine, args=(), daemon=True,
                name=f"ZmqMultiRequestsReceiver-worker-{i}"
            )
            worker.start()
            self.workers.append(worker)

    def _listen(self) -> None:
        try:

            # log.debug("ZMQ creating router and dealer sockets...")
            self.router_socket = self.zmq_context.socket(zmq.ROUTER)
            self.router_socket.bind(
                f"tcp://{self.socket_address[0]}:{self.socket_address[1]}"
            )

            self.dealer_socket = self.zmq_context.socket(zmq.DEALER)
            self.dealer_socket.bind("inproc://workers")

            # log.debug("ZMQ creating proxy...")
            zmq.proxy(self.router_socket, self.dealer_socket)
            # log.debug("ZMQ created proxy!")

        except Exception as error:
            if not self._terminate:
                log.error(str(error))
        finally:
            # log.debug("ZMQ closing rouet & dealer sockets...")
            if self.router_socket:
                self.router_socket.close()
            if self.dealer_socket:
                self.dealer_socket.close()

    def _worker_routine(self) -> None:
        """Worker thread routine to handle requests."""
        worker_socket = self.zmq_context.socket(zmq.DEALER)
        worker_socket.connect("inproc://workers")

        while not self._terminate:
            identity, _, request = worker_socket.recv_multipart()
            if request == TERMINATTION_CODE:
                self._terminate = True
            if self._terminate:
                worker_socket.close()
                return
            # log.debug("ZMQ worker processing request...")
            reply = self.handle_request(request)
            # log.debug("ZMQ worker sending reply...")
            worker_socket.send_multipart([identity, b"", reply])

    def terminate(self) -> None:
        """Stop listening for requests and clean up resources."""
        if self._terminate:
            return
        try:
            # log.debug("ZMQ shutting down ZmqMultiRequestsReceiver...")
            # if not self.listener_thread.is_alive():
            #     log.debug("ZMQ socket must already be shut down.")
            #
            #     return
            self._terminate = True
            # log.debug("Waiting for workers to stop...")
            while True:
                all_workers_stopped = True
                for worker in self.workers:
                    if worker.is_alive():
                        all_workers_stopped = False
                        break
                if all_workers_stopped:
                    break
                sock = self.zmq_context.socket(zmq.REQ)
                sock.setsockopt(zmq.LINGER, 1)

                sock.connect(
                    f"tcp://{self.socket_address[0]}:{self.socket_address[1]}"
                )
                sock.send("close".encode())
                sock.close()
                sleep(0.1)
            if self.router_socket:
                self.router_socket.close()
            if self.dealer_socket:
                self.dealer_socket.close()
            self.listener_thread.join()
        except Exception as error:
            log.error(
                "error in API-Terminal.ZMQ-ZmqRequestsReceiver.terminate(): "
                f"{error}"
            )
        # log.debug("ZMQ: terminating context.")
        self.zmq_context.term()

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
        if request == TERMINATTION_CODE:
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
        CONTEXTS.append(self.zmq_context)
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
            # log.debug("Shutting down ZMQ resources.")
            self.pub_socket.close()
            self.zmq_context.term()
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
                        raise OverflowError(
                            "Received more data than expected!"
                        )
                    # change the beginning time for measurement
                    begin = time.time()
        except:
            pass
    return total_data


def _tcp_send_counted(sock: socket.socket, data: bytearray | bytes) -> None:
    length = len(data)
    sock.send(to_b255_no_0s(length) + bytearray([0]))
    sock.send(data)
