"""Brenthy Core's BrenthyAPI interface.

This script contains the machinery that receives and processes incoming
BrenthyAPI remote procedure calls (RPCs) for Brenthy Core and its blockchains
from applications, as well as for publishing events from Brenthy's blockchains
to subscribed applications.
"""

import json
import os
from types import ModuleType

import blockchain_manager
from brenthy_tools_beta import log
from brenthy_tools_beta.brenthy_api import (
    BLOCKCHAIN_RETURNED_NO_RESPONSE,
    UNKNOWN_BLOCKCHAIN_TYPE,
)
from brenthy_tools_beta.utils import (
    function_name,
    load_module_from_path,
)
from brenthy_tools_beta.version_utils import decode_version, encode_version
from brenthy_tools_beta.versions import BRENTHY_CORE_VERSION

# list of files and folders in the brenthy_api_protocols folder
# which are not BrenthyAPI protocol modules
BAP_EXCLUDED_MODULES = ["__init__.py", "__main__.py", "__pycache__", ".tmp"]
bap_protocol_modules: list[ModuleType] = []


def get_brenthy_version(_: bytes) -> bytes:
    """(Brenthy RPC): Get Brenthy Core's version."""
    return json.dumps({"brenthy_core_version": BRENTHY_CORE_VERSION}).encode()


def brenthy_request_handler(request: bytes) -> bytes:
    """Process RPCs made to Brenthy."""
    function = request[: request.index(bytearray([0]))].decode()
    payload = request[request.index(bytearray([0])) + 1:]
    if function == "get_brenthy_version":
        return get_brenthy_version(payload)
    else:
        log.warning(
            "api_terminal: Received request that was not understood: "
            + function
            + " "
            + str(payload)
        )
        return json.dumps(
            {"success": False, "error": "not understood"}
        ).encode()


def request_router(request: bytearray, blockchain_type: str) -> bytearray:
    """Forward a BrenthyAPI RPC to the Brenthy or the correct blockchain.

    This function processes requests incoming from the apps,
    relaying them to the correct specialised task-specific handlers.
    """
    if blockchain_type == "Brenthy":
        return bytearray([1]) + brenthy_request_handler(request)
    for blockchain_module in blockchain_manager.blockchain_modules.values():
        if blockchain_module.blockchain_type == blockchain_type:
            reply = blockchain_module.api_request_handler(request)
            if reply:
                # bytearray([1]) signals success
                return bytearray([1]) + reply

            log.warning(
                f"Blockchain type {blockchain_type} returned a null "
                "response to a brenthy_api request."
            )
            # bytearray([0]) signals failure
            return bytearray([0]) + json.dumps(
                {"error": BLOCKCHAIN_RETURNED_NO_RESPONSE}
            ).encode()

    # bytearray([0]) signals failure
    return bytearray([0]) + json.dumps({
        "success": False,
        "error": UNKNOWN_BLOCKCHAIN_TYPE,
        "blockchain_type": blockchain_type,
    }).encode()


def handle_request(request: bytearray) -> bytearray:
    """Handle RPC requests made via BrenthyAPI.

    Extract's encoded brenthy_tools.brenthy_api version from requests,
    passes on the requests to request_router for processing,
    and encode our Brenthy-Core version into the response.
    """
    # try to decapsulate request and pass it on to its destination
    try:
        # extract brenthy_tools version
        brenthy_tools_version = decode_version(  # pylint: disable=unused-variable
            request[: request.index(bytearray([0]))]
        )
        request = request[request.index(bytearray([0])) + 1:]

        # extract blockchain type
        blockchain_type = request[: request.index(bytearray([0]))].decode()
        payload = request[request.index(bytearray([0])) + 1:]

        # forward request to its destination blockchain type or brenthy
        reply = request_router(payload, blockchain_type)

    except Exception as e:  # pylint: disable=broad-exception caught
        log.error(
            f"Unhandled Exception in api_terminal.{function_name()}:\n"
            f"{str(request)}\n{e}"
        )
        # bytearray([0]) signals failure
        reply = (
            bytearray([0])
            + json.dumps({
                "success": False,
                "error": "Internal Brenthy error. Check Brenthy log to debug.",
            }).encode()
        )

    # encapsulate reply in message with the Brenthy Core version
    reply = encode_version(BRENTHY_CORE_VERSION) + bytearray([0]) + reply
    return reply


def publish_event(
    blockchain_type: str, payload: dict, topics: list[str] | None = None
) -> None:
    """Publish a blockchain type's message to all subscribed applications."""
    if not isinstance(blockchain_type, str):
        error_message = (
            "api_terminal.publish_event: Parameter blockchain_type must be of "
            f"type str, not {type(blockchain_type)}"
        )
        log.error(error_message)
        raise TypeError(error_message)
    if blockchain_type not in blockchain_manager.blockchain_modules.keys():
        error_message = (
            "api_terminal.publish_event: "
            "The blockchain_type provided does not exist."
        )
        log.error(error_message)
        raise ValueError(error_message)
    if not isinstance(payload, dict):
        error_message = (
            "api_terminal.publish_event: Parameter payload must be of type "
            f"dict, not {type(payload)}"
        )
        log.error(error_message)
        raise TypeError(error_message)
    if isinstance(topics, str):
        topics = [topics]
    elif topics is None:
        topics = []
    elif not isinstance(topics, list):
        error_message = (
            "api_terminal.publish_event: Parameter topics must be of type "
            f"list or str, not {type(payload)}"
        )
        log.error(error_message)
        raise TypeError(error_message)

    if "topic" in payload.keys():
        error_message = (
            "api_terminal.publish_event: Parameter payload may not have the "
            "topic key defined, api_terminal.publish_event() needs to use that"
            " key name. Use another key name for your purposes."
        )
        log.error(error_message)
        raise ValueError(error_message)

    for topic in topics:
        data = {"topic": f"{blockchain_type}-{topic}"}
        data.update(payload)
        log.info("api_terminal.publish_event: " + f"{blockchain_type}-{topic}")
        publish_on_all_endpoints(data)


def load_brenthy_api_protocols() -> None:  # pylint: disable=unused-variable
    """Load the BrenthyAPI modules."""
    global bap_protocol_modules  # pylint: disable=global-statement
    bap_protocol_modules = []
    protocols_path = os.path.join(
        os.path.dirname(__file__), "brenthy_api_protocols"
    )
    try:
        for filename in os.listdir(protocols_path):
            if filename in BAP_EXCLUDED_MODULES:
                continue
            bap_protocol_modules.append(
                load_module_from_path(os.path.join(protocols_path, filename))
            )
    except AttributeError:
        log.error(

            "api_terminal.load_brenthy_api_protocols(): couldm't load all "
            f"modules in {protocols_path}. "
            "Make sure there are no files there other than "
            "BrenthyAPI protocol modules, or add other files to the constant"
            f"{BAP_EXCLUDED_MODULES} in Brenthy/api_terminal/api_terminal.py"

        )


def start_listening_for_requests() -> None:
    """Asynchronously run the ZMQ and TCP listeners for App Requests."""
    for protocol in bap_protocol_modules:
        log.info(f"Initialising BAP protocol {protocol.BAP_VERSION}")
        protocol.initialise()


def publish_on_all_endpoints(data: dict) -> None:
    """Publish a message using all BrenthyAPI modules."""
    for protocol in bap_protocol_modules:
        protocol.publish(data)


def terminate() -> None:  # pylint: disable=unused-variable
    """Shut down BrenthyAPI communications, cleaning up resources."""
    for protocol in bap_protocol_modules:
        protocol.terminate()
