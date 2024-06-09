"""Brenthy API Protocol version 2, on Brenthy-Core's side.

This module contains the machinery used by Brenthy Core for BrenthyAPI
communication, using the version 1 BrenthyAPI Protocol.
This module's counterpart, which contain's brenthy tool's machinery, is at
../../brenthy_tools_beta/brenthy_api_protocols/bap_4_brenthy_tools.py
"""

import api_terminal
from api_terminal.bat_endpoints import ZmqMultiRequestsReceiver, ZmqPublisher
from brenthy_tools_beta import log
from brenthy_tools_beta.brenthy_api_addresses import (
    BAP_4_PUB_ADDRESS,
    BAP_4_RPC_ADDRESS,
)

BAP_VERSION = 4  # pylint: disable=unused-variable

zmq_listener: ZmqMultiRequestsReceiver | None = None
pub_socket: ZmqPublisher | None = None


def initialise() -> None:  # pylint: disable=unused-variable
    """Start listening for RPC requests."""
    global pub_socket  # pylint: disable=global-statement
    global zmq_listener  # pylint: disable=global-statement

    # Pass ZMQ requests to delegator, which opens new socket, and responds with
    # its port number. The other socket waits for the RPC to finish and sends
    # its result to the requester, so that this RequestsReceiver doesn't get
    # blockced waiting for the RPC to complete.
    log.info("BAP-4 ZMQ creating listener...")
    zmq_listener = ZmqMultiRequestsReceiver(
        BAP_4_RPC_ADDRESS,
        api_terminal.handle_request,
    )
    pub_socket = ZmqPublisher(BAP_4_PUB_ADDRESS)


def terminate() -> None:  # pylint: disable=unused-variable
    """Stop listening for RPC requests and clean up resources."""
    if zmq_listener:
        log.info("BAP-4 ZMQ terminating listener socket.")
        zmq_listener.terminate()
    if pub_socket:
        log.info("BAP-4 ZMQ terminating PubSub socket..")
        pub_socket.terminate()


def publish(data: dict) -> None:  # pylint: disable=unused-variable
    """Publish data via pubsub."""
    if not pub_socket:
        error_message = (
            "bap_4_brenthy_core.publish(): socket hasn't been initialised"
        )
        log.error(error_message)
        return
    # log.debug("BAP-4 ZMQ publishing...")
    pub_socket.publish(data)
    # log.debug("BAP-4 ZMQ published!")
