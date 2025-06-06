"""Brenthy API Protocol version 1, on Brenthy-Core's side.

This module contains the machinery used by Brenthy Core for BrenthyAPI
communication, using the version 1 BrenthyAPI Protocol.
This module's counterpart, which contain's brenthy tool's machinery, is at
../../brenthy_tools_beta/brenthy_api_protocols/bap_3_brenthy_tools.py
"""

import api_terminal
from api_terminal.bat_endpoints import TcpMultiRequestsReceiver
from brenthy_tools_beta.brenthy_api_addresses import (
    BRENTHY_API_IP_LISTEN_ADDRESS, BAP_3_RPC_PORT,
)
from brenthy_tools_beta import log

BAP_VERSION = 3  # pylint: disable=unused-variable


tcp_listener: TcpMultiRequestsReceiver | None = None


def initialise() -> None:  # pylint: disable=unused-variable
    """Start listening for RPC requests."""
    global tcp_listener  # pylint: disable=global-statement

    tcp_listener = TcpMultiRequestsReceiver(
        (BRENTHY_API_IP_LISTEN_ADDRESS, BAP_3_RPC_PORT),
        api_terminal.handle_request,
    )
    log.important(f"API listening on {tcp_listener.socket_address}")


def terminate() -> None:  # pylint: disable=unused-variable
    """Stop listening for RPC requests and clean up resources."""
    if tcp_listener:
        tcp_listener.terminate()


def publish(data: dict) -> None:  # pylint: disable=unused-variable,unused-argument
    """NOT IMPLEMENTED: publish data via pubsub."""
