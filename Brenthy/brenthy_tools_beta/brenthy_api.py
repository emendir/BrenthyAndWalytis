"""Library for interacting with Brenthy Core and its blockchain types."""

from .brenthy_api_protocols import BAP_MODULES_REGISTRY
import importlib
import json
import os
from inspect import signature
from types import FunctionType, ModuleType

from brenthy_tools_beta import bt_endpoints, log
from brenthy_tools_beta.bt_endpoints import CantConnectToSocketError
from brenthy_tools_beta.utils import function_name, load_module_from_path
from brenthy_tools_beta.version_utils import (
    decode_version,
    encode_version,
    version_to_string,
)
from brenthy_tools_beta.versions import BRENTHY_TOOLS_VERSION
from . import brenthy_api_addresses
BLOCKCHAIN_RETURNED_NO_RESPONSE = "blockchain returned no response"
UNKNOWN_BLOCKCHAIN_TYPE = "unknown blockchain type"


# list of files and folders in the brenthy_api_protocols folder
# which are not BrenthyAPI protocol modules
BAP_EXCLUDED_MODULES = ["__init__.py", "__main__.py", "__pycache__", ".tmp"]

bap_protocol_modules: list[ModuleType] = []

log.LOG_FILENAME = ".brenthy_api.log"
log.LOG_ARCHIVE_DIRNAME = ".brenthy_api_log_archive"


def _load_brenthy_api_protocols_from_files() -> None:
    # files in the current directory which don't define bap_protocol_modules
    global bap_protocol_modules  # pylint: disable=global-statement
    bap_protocol_modules = []
    protocols_path = os.path.join(
        os.path.dirname(__file__), "brenthy_api_protocols"
    )
    for filename in os.listdir(protocols_path):
        if filename in BAP_EXCLUDED_MODULES:
            continue
        try:
            bap_protocol_modules.append(
                load_module_from_path(os.path.join(protocols_path, filename))
            )
        except:
            error_message = (
                "BrenthyAPI: Failed to load Brenthy API Protocol module "
                f"{filename}"
            )
            log.error(error_message)
            # raise ImportError(error_message)
    # sort bap modules in order of BAP version, newest to oldest
    bap_protocol_modules.sort(key=lambda x: x.BAP_VERSION, reverse=True)


def _load_brenthy_api_protocols_from_registry() -> None:

    bap_protocol_modules = []
    for module_name in BAP_MODULES_REGISTRY:
        if module_name in BAP_EXCLUDED_MODULES:
            continue
        module = importlib.import_module(
            f"..brenthy_api_protocols.{module_name}", package=__name__
        )
        bap_protocol_modules.append(module)
    bap_protocol_modules.sort(key=lambda x: x.BAP_VERSION, reverse=True)


def _load_brenthy_api_protocols() -> None:
    _load_brenthy_api_protocols_from_files()


def send_request(
    blockchain_type: str, payload: bytearray | bytes
) -> bytearray:
    """Send a request to Brenthy or one of its installed blockchain types.

    Args:
        blockchain_type(str): the blockchain type to forward the payload to
            use 'Brenthy' if the request is to Brenthy itself
        payload(bytearray): the message to send to Brenthy or the blockchain
    Returns:
        bytearray: the reply from Brenthy or the blockchain.
    """
    if isinstance(payload, bytes):
        payload = bytearray(payload)
    if not isinstance(blockchain_type, str):
        error_message = (
            "blockchain_type must be of type str, not "
            f"{type(blockchain_type)}"
        )
        log.error(f"BrenthyAPI: {function_name()}: {error_message}")
        raise TypeError(error_message)
    if not isinstance(payload, bytearray):
        error_message = (
            "payload must be of type bytearray, not " f"{type(payload)}"
        )
        log.error(f"BrenthyAPI: {function_name()}: {error_message}")
        raise TypeError(error_message)

    # encapsulate the request together with the blockchain type
    # and brenthy_tools version
    request = blockchain_type.encode() + bytearray([0]) + payload
    request = encode_version(BRENTHY_TOOLS_VERSION) + bytearray([0]) + request

    reply: bytearray = bytearray()
    # whether or not we've managed to establish communication with Brenthy-Core
    communicated = False
    # try sending request via different protocols
    for protocol in bap_protocol_modules:
        try:
            reply = protocol.send_request(request)
        except CantConnectToSocketError:
            # try next BrenthyAPI protocol
            continue
        communicated = True

        # decapsulate the reply
        try:
            brenthy_core_version = decode_version(
                reply[: reply.index(bytearray([0]))]
            )
            reply = reply[reply.index(bytearray([0])) + 1:]
            if not reply:
                continue
            # Request was processed successfully by Brenthy.
            success = reply[0] == 1
            reply = reply[1:]

            break  # request sent, got reply,so move on
        except:
            continue
    if not reply:
        if communicated:
            raise BrenthyReplyDecodeError(
                BrenthyReplyDecodeError.def_message
                + "\nThe reply received was empty."
            )
        else:
            raise BrenthyNotRunningError()
    if success:
        return reply

    # Brenthy/blockchain failed to process our request.
    raise _analyse_no_success_reply(reply)


def _analyse_no_success_reply(reply: bytearray) -> Exception:
    """Get the appropriate Exception for the given reply from Brenthy.

    Assumes the reply is from a request which Brenthy (not its blockchains)
    failed to execute.

    Args:
        reply (bytearray): the response from Brenthy for the failed RPC
    """
    if not reply:
        return BrenthyReplyDecodeError(
            "Received empty JSON reply from Brenthy.", reply=data
        )
    data = None
    try:
        data = json.loads(reply.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return BrenthyReplyDecodeError(
            "Failed to decode Brenthy's binary reply to JSON.", reply=reply
        )  # pylint: disable=
    if not data:
        return BrenthyReplyDecodeError(
            "Received empty JSON reply from Brenthy.", reply=data
        )
    if "error" in data.keys():
        if data["error"] == BLOCKCHAIN_RETURNED_NO_RESPONSE:
            error_message = "Blockchain returned no response to request."
            log.error(f"BrenthyAPI: {function_name()}: {error_message}")
            return BrenthyError("Blockchain returned no response to request.")
        if data["error"] == UNKNOWN_BLOCKCHAIN_TYPE:
            error_message = "Unknown blockchain type."
            log.error(f"BrenthyAPI: {function_name()}: {error_message}")
            return UnknownBlockchainTypeError(
                blockchain_type=data["blockchain_type"]
            )
    return BrenthyReplyDecodeError(
        "Failed to decode Brenthy's reply. "
        "It indicated failure, but included no error message.",
        reply=data,
    )


def send_brenthy_request(function_name: str, payload: bytearray) -> bytearray:
    """Make a request to Brenthy (NOT a Brenthy blockchain).

    Args:
        function_name (str): the name of the function in api_terminal
                                which we want to call
        payload (bytearray): the data the function in api_terminal
                                needs to process our request, its arguments
    Returns:
        bytearray: the reply from the function we called in
                                api_terminal
    """
    request = function_name.encode() + bytearray([0]) + payload
    return send_request("Brenthy", request)


class EventListener:
    """Class for listening to the messages published by a blockchain type."""

    def __init__(
        self,
        blockchain_type: str,
        eventhandler: FunctionType,
        topics: str | list[str],
    ):
        """Listen messages published by a blockchain type.

        Args:
            blockchain_type (str): the blockchain type whose messages to listen
                                    to
            eventhandler (FunctionType): the function to be called when a
                                    message is received
            topics (list[str] | str): the topic or topic to filter the
                                    blockchain type's publication's by
        """
        if not topics:
            topics = []
        if isinstance(topics, str):
            topics = [topics]
        if not isinstance(topics, list):
            error_message = (
                f"BrenthyAPI: EventListener("
                f"{topics}): Parameter topics must be of type list or str, "
                f"not {type(topics)}"
            )
            log.error(error_message)
            raise ValueError(error_message)
        self.blockchain_type = blockchain_type
        brenthy_topics = [
            f"{self.blockchain_type}-{topic}" for topic in topics
        ]
        self.users_eventhandler = eventhandler

        eventlistener: bt_endpoints.EventListener
        # go through the different BrenthyAPI Protocols, newest version first,
        # until one succeeds at connecting an EventListener to Brenthy
        for protocol in bap_protocol_modules:
            try:
                eventlistener = protocol.EventListener(
                    self._handler, brenthy_topics
                )
            except (CantConnectToSocketError, NotImplementedError):
                # try next BrenthyAPI protocol
                continue
            break  # EventListener connected

        if not eventlistener:
            raise BrenthyNotRunningError

        self._eventlistener = eventlistener

    def _handler(self, message: dict, topic: str) -> None:
        """Process an event from Brenthy Core."""
        topic = topic.strip(f"{self.blockchain_type}-")
        # call the eventhandler, passing it the data and topic
        n_params = len(signature(self.users_eventhandler).parameters)
        if n_params == 1:
            self.users_eventhandler(
                message,
            )
        else:
            self.users_eventhandler(message, topic)

    def terminate(self) -> None:
        """Stop listening to publications and clean up resources."""
        self._eventlistener.terminate()

    def __del__(self):
        """Stop listening to publications and clean up resources."""
        self.terminate()


# pylint: disable=unused-variable


def get_brenthy_version() -> tuple:
    """Get the software version of the locally running Brenthy node.

    Returns:
        tuple: the software version of the locally running Brenthy node
    """
    return tuple(
        json.loads(
            send_brenthy_request("get_brenthy_version", bytearray([])).decode()
        )["brenthy_core_version"]
    )


def get_brenthy_version_string() -> str:
    """Get the software version of the locally running Brenthy node.

    Returns:
        str: the software version of the locally running Brenthy node
    """
    return version_to_string(get_brenthy_version())


def get_brenthy_tools_beta_version() -> tuple:
    """Get the software version of the this brenthy_tools_beta library.

    Returns:
        tuple: the software version of the this brenthy_tools_beta library
    """
    return BRENTHY_TOOLS_VERSION


def get_brenthy_tools_beta_version_string() -> str:
    """Get the software version of the this brenthy_tools_beta library.

    Returns:
        str: the software version of the this brenthy_tools_beta library
    """
    return version_to_string(get_brenthy_tools_beta_version())


class BrenthyNotRunningError(Exception):
    """When no communication can be established with Brenthy."""

    def_message = f"""
Can't connect to Brenthy at {brenthy_api_addresses.BRENTHY_IP_ADDRESS}.
Is it running?
If running Brenthy using a docker container, you probably need to set:
```py
brenthy_tools_beta.brenthy_api_addresses.BRENTHY_IP_ADDRESS=DOCKER_CONTAINER_IP
```
"""

    def __init__(self, message: str = def_message):
        """Raise a BrenthyNotRunningError exception.

        Args:
            message (str): the error message to store in this Exception
        """
        self.message = message

    def __str__(self):
        """Get this exception's error message."""
        return self.message


class BrenthyReplyDecodeError(Exception):
    """When Brenthy's reply can't be decoded."""

    def_message = (
        "error parsing the reply from Brenthy. " "This is probably a bug."
    )

    def __init__(self, message: str = def_message, reply: bytearray | None = None):
        """Raise a BrenthyReplyDecodeError exception.

        Args:
            message (str): the error message to store in this Exception
            reply (str): the reply received from Brenthy
        """
        self.message = message
        self.reply = str(reply)

    def __str__(self):
        """Get this exception's error message."""
        return self.message + " \n" + self.reply


class BrenthyError(Exception):
    """When Brenthy runs into an error processing a request (Brenthy bug)."""

    def_message = (
        "Brenthy (NOT brenthy_api) failed to process our request. "
        "This is probably a bug."
    )

    def __init__(self, message: str = def_message):
        """Raise a BrenthyError exception.

        Args:
            message (str): the error message to store in this Exception
        """
        self.message = message

    def __str__(self):
        """Get this exception's error message."""
        return self.message


class UnknownBlockchainTypeError(Exception):
    """When the provided blockchain type isn't installed on Brenthy."""

    def_message = (
        "We don't know this type of blockchain. "
        "Perhaps give Brenthy a chance to update by restarting it."
    )

    def __init__(self, message: str = def_message, blockchain_type: str = ""):
        """Raise a UnknownBlockchainTypeError exception.

        Args:
            message (str): the error message to store in this Exception
            blockchain_type (str): the unknown blockchain type
        """
        self.message = message
        self.blockchain_type = blockchain_type

    def __str__(self):
        """Get this exception's error message."""
        if self.blockchain_type:
            self.message = self.blockchain_type + ": " + self.message
        return self.message

_AUTO_LOAD_BAP_MODULES = os.environ.get("AUTO_LOAD_BAP_MODULES", "").lower()
if not _AUTO_LOAD_BAP_MODULES or _AUTO_LOAD_BAP_MODULES in ["true", "1"]:
    AUTO_LOAD_BAP_MODULES = True
elif _AUTO_LOAD_BAP_MODULES in ["false", "0"]:
    AUTO_LOAD_BAP_MODULES = False
else:
    error_message = (
        "Invalid value for environment variable AUTO_LOAD_BAP_MODULES: "
        f"{_AUTO_LOAD_BAP_MODULES}\n"
        "Valid values: 0, false, False, 1, true, True"
    )

if AUTO_LOAD_BAP_MODULES:
    _load_brenthy_api_protocols()
