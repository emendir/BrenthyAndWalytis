"""Brenthy API Protocol version 1, on Brenthy-Tool's side.

This module contains the machinery used by brenthy_tools.brenthy_api for
BrenthyAPI communication with Brenthy Core, using the version 1 BrenthyAPI
Protocol.
This module's counterpart, which contain's Brenthy Core's machinery, is at
../../api_terminal/brenthy_api_protocols/bap_3_brenthy_core.py
"""

from brenthy_tools_beta import bt_endpoints
from brenthy_tools_beta.brenthy_api_addresses import (
    BRENTHY_IP_ADDRESS, BAP_3_RPC_PORT
)
from brenthy_tools_beta.bt_endpoints import send_request_tcp

BAP_VERSION = 3  # pylint: disable=unused-variable


def send_request(request: bytearray | bytes) -> bytes:  # pylint: disable=unused-variable
    """Send a BrenthyAPI request to Brenthy-Core, returning its reply.

    Args:
        request (bytearray): the data to send to Brenthy-Core
    Returns:
        bytearray: the response received from Brenthy-Core
    """
    return send_request_tcp(
        request,
        (BRENTHY_IP_ADDRESS, BAP_3_RPC_PORT),
    )


class EventListener(bt_endpoints.EventListener):  # pylint: disable=unused-variable,too-few-public-methods
    """NOT IMPLEMENTED: for listening to events published by Brenthy Core."""

    def __init__(self, *args):
        """NOT IMPLEMENTED: Listen for events from Brenthy Core."""
        raise NotImplementedError
