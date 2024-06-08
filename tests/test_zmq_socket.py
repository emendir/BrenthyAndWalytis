import zmq
import time
from threading import Thread
import logging
import os
import sys
from datetime import datetime
if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    import run
    from api_terminal.bat_endpoints import ZmqMultiRequestsReceiver
    from brenthy_tools_beta import brenthy_api
    from brenthy_tools_beta.utils import time_to_string

# Set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def handle_request(request: bytes) -> bytes:
    """Example request handler that simulates processing time."""
    time.sleep(2)  # Simulate some processing time
    return b"Response to: " + request


def client_task(identity: int, address: str):
    """Client task that sends a request and waits for a reply."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.identity = f"client-{identity}".encode('ascii')
    socket.connect(address)

    print(f"{time_to_string(datetime.now())}: Client {identity} sending request")
    socket.send(b"Hello")
    reply = socket.recv()
    print(f"{time_to_string(datetime.now())}: Client {identity} received reply: {reply}")


def run_test():
    """Run the test to demonstrate handling of 10 concurrent requests."""
    server_address = 'tcp://127.0.0.1:5555'
    receiver = ZmqMultiRequestsReceiver(
        ('127.0.0.1', 5555), handle_request, max_parallel_handlers=5)

    client_threads = []
    for i in range(10):
        client_thread = Thread(target=client_task, args=(i, server_address))
        client_threads.append(client_thread)
        client_thread.start()

    for client_thread in client_threads:
        client_thread.join()

    receiver.terminate()


if __name__ == "__main__":
    run_test()
