"""The machinery for communicating with Brenthy Core.

It contains functions that are a direct part of Walytis_Beta API and intended
for use by the Walytis_Beta API user (e.g. the create_blockchain() function),
but also functions that are used only by higher-level WalytisAPI constructs
such as BlocksListener class, which is not intended for use by the Walytis API
user, but is used by the blockchain_model.Blockchain class instead,
which is in turn intended for use by the Walytis_Beta API user.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Callable

import ipfs_api
from brenthy_tools_beta import brenthy_api, log
from brenthy_tools_beta.utils import (
    bytes_to_string,
    decode_timestamp,
    from_b255_no_0s,
    function_name,
    string_to_bytes,
    to_b255_no_0s,
)
from brenthy_tools_beta.version_utils import (
    decode_version,
    encode_version,
    version_to_string,
)

from .block_model import (
    Block,
    decode_short_id,  # pylint: disable=unused-import
    short_from_long_id
)
from .exceptions import (
    BlockchainAlreadyExistsError,
    BlockIntegrityError,
    BlockNotFoundError,
    JoinFailureError,
    NoSuchBlockchainError,
    NoSuchInvitationError,
    WalytisBugError,
    WalytisReplyDecodeError,
)
from .versions import (
    WALYTIS_BETA_API_PROTOCOL_VERSION,
    WALYTIS_BETA_API_VERSION,
)

# storing this blockchain's name so that we don't missspell it
WALYTIS_BETA = "Walytis_Beta"


# --------------Settings ---------------------------
log.PRINT_DEBUG = False


NO_SUCH_BLOCKCHAIN_MESSAGE = "no such blockchain"
NO_SUCH_INVITATION_MESSAGE = "no such join-key"
BLOCK_NOT_FOUND = "block not found"
WALYTIS_BETA_ERROR_MESSAGE = "internal Walytis_Beta error"
BLOCKCHAIN_EXISTS_MESSAGE = "blockchain already exists"

# -------------- User Functions --------------------

# --- Blockchain IDs and Names ---


def list_blockchains(names_first: bool = False) -> list[tuple[str, str]]:
    """Get the IDs names of all the blockchains we have.

    Args:
        names_first: determines the order of the the tuple contents in the
                        return value. See Returns.

    Returns:
        list: A list of tuples of the names and IDs of all the Walytis_Beta
                blockchains we have. Tuples are (id, name) by default,
                but (name, id) if names_first == True
    """
    # make request to Brenthy
    _response = _send_request("list_blockchains", bytearray([]))

    # read and process response from Brenthy
    try:
        response = json.loads(_response.decode())

        # handle unexpected response type
        if not isinstance(response, list):
            _error = _read_appcomterm_error_message(response)
            log.error(f"WAPI: {function_name()}: {str(_error)}")
            raise _error

        if names_first:
            return [(name, id) for id, name in response]
        else:
            # convert lists to tuples
            return [(id, name) for id, name in response]

    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def list_blockchain_names() -> list[str]:
    """Get the names of all the blockchains we have.

    Returns:
        list: A list of the names of all the Walytis_Beta blockchains we have.
    """
    return [name for id, name in list_blockchains()]


def list_blockchain_ids() -> list[str]:
    """Get the ids of all the blockchains we have.

    Returns:
        list: A list of the names of all the Walytis_Beta blockchains we have.
    """
    return [id for id, name in list_blockchains()]


def get_blockchain_id(blockchain_name: str | bytearray) -> str:
    """Given a blockchain's name, returns its ID.

    If a blockchain's ID is given, it returns the ID.

    Args:
        blockchain_name (str): the name of the blockchain to look up
    Returns:
        str: the ID of the blockchain
    """
    blockchains = list_blockchains()

    # if a blockchain id was passed
    if blockchain_name in [id for id, name in blockchains]:
        return blockchain_name
    for id, name in blockchains:
        if name == blockchain_name:
            return id
    error = NoSuchBlockchainError(blockchain_name=blockchain_name)
    log.error(f"WAPI: {function_name()}: {str(error)}")
    raise error


def get_blockchain_name(blockchain_id: str) -> str:
    """Given a blockchain's id, returns its name.

    If a blockchain's name is given, it returns the name.

    Args:
        blockchain_id (str): the id of the blockchain to look up
    Returns:
        str: the name of the blockchain
    """
    blockchains = list_blockchains()

    # if a blockchain id was passed
    for id, name in blockchains:
        if blockchain_id == id:
            return name

    # if a blockchain name was passed
    if blockchain_id in [name for id, name in blockchains]:
        return blockchain_id
    error = NoSuchBlockchainError(blockchain_id=blockchain_id)
    log.error(f"WAPI: {function_name()}: {str(error)}")
    raise error


# --- Blockchain Lifecycle ---


def create_blockchain(blockchain_name: str = "") -> str:
    """Create and run a new blockchain.

    Args:
        blockchain_name (str): blockchain's local name: a human-readable label
                to ease recognition when manually interacting with Walytis_API.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.

    Returns:
        str: ID of the created blockchain
    """
    payload = json.dumps({"blockchain_name": blockchain_name}).encode()

    _response = _send_request("create_blockchain", payload)
    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        success = response["success"]
    except Exception:
        error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    if not success:
        error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    blockchain_id = response["blockchain_id"]

    return blockchain_id


def join_blockchain(invitation: str, blockchain_name: str = "") -> str:
    """Join a blockchain using an invitation generated by a blockchain node.

    Args:
        invitation (str): the invitation generated by a blockchain member
        blockchain_name (str): blockchain's local name: a human-readable label
                to ease recognition when manually interacting with WalytisAPI.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.

    Returns:
        str: the ID of the joined blockchain
    """
    # convert invitation from JSON string to dict
    if isinstance(invitation, str):
        invitation = json.loads(invitation)
    if not isinstance(invitation, dict):
        raise ValueError(
            "The parameter invitation must be of type str or dict,"
            + f" not {type(invitation)}"
        )
    log.debug(f"WAPI: {function_name()}: ")
    # invitation is now of type dict
    blockchain_id = invitation["blockchain_id"]

    blockchains = list_blockchains()

    if blockchain_id in [id for id, name in blockchains]:
        error = BlockchainAlreadyExistsError(blockchain_id=blockchain_id)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    if blockchain_name in [name for id, name in blockchains]:
        error = BlockchainAlreadyExistsError(blockchain_name=blockchain_name)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    log.debug(f"WAPI: {function_name()}: Making request...")

    response = json.loads(
        _send_request(
            "join_blockchain",
            json.dumps(
                {
                    "invitation": invitation,
                    "blockchain_name": blockchain_name,
                }
            ).encode(),
        ).decode()
    )
    log.debug(f"WAPI: {function_name()}: Got response!")

    if response["success"]:
        return blockchain_id
    else:
        error = ""
        if "error" in response.keys():
            error = response["error"]
        error = JoinFailureError(error_message=error)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error


def join_blockchain_from_zip(
    blockchain_id: str, blockchain_data_path: str, blockchain_name: str = ""
) -> None:
    """Join an existing live blockchain, given a zip file of all its data.

    Args:
        blockchain_id (str): the name of the blockchain
        blockchain_data_path (str): path of the zip file containing the
                blockchain's data
        blockchain_name (str): blockchain's local name: a human-readable label
                to ease recognition when manually interacting with WalytisAPI.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.
    """
    log.debug(f"WAPI: {function_name()}: Unpacking appdata...")

    import tempfile

    tempdir = tempfile.mkdtemp()
    # extract zip file
    shutil.unpack_archive(
        os.path.abspath(blockchain_data_path), tempdir, "zip"
    )
    log.debug(f"WAPI: {function_name()}: Publishing on IPFS...")

    # if the appdata is in the zip file's root directory
    if os.path.exists(os.path.join(tempdir, "KnownBlocksIndex")):
        cid = ipfs_api.publish(tempdir)
    # if the appdata folder is a folder inside the zip file's
    elif os.path.exists(
        os.path.join(tempdir, blockchain_id, "KnownBlocksIndex")
    ):
        cid = ipfs_api.publish(os.path.join(tempdir, blockchain_id))
    else:
        error_message = (
            "The provided appdata zip file doesn't contain readable "
            "blockchain appdata"
        )
        log.error(error_message)
        raise JoinFailureError(error_message=error_message)
    shutil.rmtree(tempdir)
    log.debug(f"WAPI: {function_name()}: Ready to join blockchain...")

    return join_blockchain_from_cid(blockchain_id, cid, blockchain_name)


def join_blockchain_from_cid(
    blockchain_id: str, blockchain_data_cid: str, blockchain_name: str = ""
) -> None:
    """Join an existing live blockchain, given the IPFS CID of its appdata.

    Args:
        blockchain_id (str): the name of the blockchain
        blockchain_data_cid (str): IPFS CID of the zip file containing the
                blockchain's data
        blockchain_name (str): blockchain's local name: a human-readable label
                to ease recognition when manually interacting with WalytisAPI.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.
    """
    blockchains = list_blockchains()

    if blockchain_id in [id for id, name in blockchains]:
        error = BlockchainAlreadyExistsError(blockchain_id=blockchain_id)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    if blockchain_name in [name for id, name in blockchains]:
        error = BlockchainAlreadyExistsError(blockchain_name=blockchain_name)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    request = json.dumps(
        {
            "blockchain_id": blockchain_id,
            "blockchain_name": blockchain_name,
            "blockchain_data_cid": blockchain_data_cid,
        }
    ).encode()
    log.debug(f"WAPI: {function_name()}: Making request...")

    _response = _send_request("join_blockchain_from_cid", request)
    log.debug(f"WAPI: {function_name()}: Got Response!")

    try:
        response = json.loads(_response.decode())
        success = response["success"]
    except Exception:
        _error = _read_appcomterm_error_message(
            response, default_error=JoinFailureError()
        )
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error
    if not success:
        raise JoinFailureError


def delete_blockchain(blockchain_id: str) -> None:
    """Delete the blockchain with the given id or name.

    Args:
        blockchain_id (str): the id or name of the blockchain to delete
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    payload = blockchain_id.encode()

    _response = _send_request("delete_blockchain", payload)

    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        success = response["success"]
    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error
    if not success:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def create_block(
    blockchain_id: str,
    content: bytearray | bytes,
    topics: list[str] | str | None = None
) -> Block:
    """Create a block with the given content on the specified blockchain.

    Args:
        blockchain_id (str): the id or name of the blockchain to create a block
        content (bytearray): the content to store on the blockchain
        topics (list): user's metadata to encode in the block's ID
    Returns:
        Block: the newly created block
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    if not (isinstance(content, (bytearray, bytes))):
        error = ValueError("Block content must be of type bytes or bytearray.")
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    if isinstance(topics, str):
        topics = [topics]
    if topics is None:
        topics = []

    response = {}

    data = blockchain_id.encode() + bytearray([0])

    data += to_b255_no_0s(len(topics)) + bytearray([0])
    for topic in topics:
        data = data + topic.encode() + bytearray([0, 0, 0])

    # adding the self's content
    data = data + content

    # askig the blockchain to build and publish the block
    response = json.loads(_send_request("create_block", data).decode())

    # if the blockchain says it failed to build the block
    if not response.get("success"):
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error

    block = get_and_read_block(
        string_to_bytes(response["block_id"])
    )  # decode the block

    return block


def get_block(blockchain_id: str, block_id: bytearray) -> Block:
    """Get a block from the specified blokchain given its block ID.

    Args:
        blockchain_id (str): the id or name of the blockchain from which to get
                                the block
        block_id (str): the id of the block
    Returns:
        Block: the Block object for the requested block
    """
    if not blockchain_id or not block_id:
        error = ValueError(
            f"The parameters can't be empty\n{blockchain_id}\n{block_id}"
        )
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    if not isinstance(blockchain_id, str):
        error_message = (
            "Walytis_BetaAPI: get_block: parameter blockchain_id must be of "
            f"type str, not {type(blockchain_id)}"
        )
        log.error(error_message)
        raise TypeError(error_message)
    if not (isinstance(block_id, (bytearray, bytes))):
        error_message = (
            "Walytis_BetaAPI: get_block: parameter block_id must "
            f"be of type bytearray or bytes, not {type(block_id)}"
        )
        log.error(error_message)
        raise TypeError(error_message)
    response = {}
    payload = json.dumps(
        {"blockchain_id": blockchain_id, "block_id": bytes_to_string(block_id)}
    ).encode()
    # askig the blockchain to build and publish the block
    response = json.loads(_send_request("get_block", payload).decode())

    # if the blockchain says it failed to build the block
    if not response.get("success"):
        _error = _read_appcomterm_error_message(
            response, default_error=BlockNotFoundError()
        )
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error

    block = get_and_read_block(
        string_to_bytes(response["block_id"])
    )  # decode the block

    return block


def is_block_known(blockchain_id: str, block_id: bytearray) -> bool:
    """Check whether or not the specified blockchain has the given block.

    Args:
        blockchain_id (str): the id or name of the blockchain to which the
                                block to look up belongs
        block_id (bytearray): the block ID to look up in the block ID records
    Returns:
        bool: Whether the block is a known block
    """
    blockchain_id = get_blockchain_id(blockchain_id)

    # Sending request to Brenthy
    payload = blockchain_id.encode() + bytearray([0]) + block_id

    # askig the blockchain to build and publish the block
    _response = _send_request("is_block_known", payload)
    response = json.loads(_response.decode())

    # Reading response from Brenthy
    if not response.get("success"):
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error
    return response["is known"]


def get_latest_blocks(
    blockchain_id: str,
    amount: int | None = None,
    since_date: datetime | None = None,
    topics: list[str] | None = None,
    long_ids: bool = False,  # defaults to False for backwards-compatibility
) -> list[bytearray]:
    """Get the latest few blocks on the blockchain.

    The amount of which is determined by the paramters.
    The blocks are returned in order of reception or creation date (CHECK!)
    from most recent to oldest.
    One of the paramaters amount or since_date must be set.

    Args:
        blockchain_id (str): the id or name of the blockchain to look up
        amount (int): how many blocks should be returned
        since_date (datetime): the maximum age of the blocks to look for.
                This function will return several even older blocks,
                some of which may have been received after the specified date
        topics (list): the topics to filter by, returning only
                blocks published on those topics, if this paramater is set.
                If not set, this function returns all blocks within the range
                of the first two parameters

    Returns:
        list: a list of IDs of the latest few blocks
    """
    blockchain_id = get_blockchain_id(blockchain_id)

    payload = json.dumps(
        {
            "blockchain_id": blockchain_id,
            "amount": amount,
            "since_date": since_date,
            "topics": topics,
            "long_ids": long_ids
        }
    ).encode()

    # send request to Brenthy
    _response = _send_request("get_latest_blocks", payload)

    # read response from Brenthy
    try:
        response = json.loads(_response.decode())
        block_ids_encoded = response.get("block_ids")
        block_ids = []
        for block_id in block_ids_encoded:
            block_ids.append(string_to_bytes(block_id))

        # BACKWARDS COMPATIBILITY foor versions of WalytisCore that don't
        # support the `long_ids` parameter:
        if bytearray([0, 0, 0, 0]) not in block_ids[0]:
            block_ids = [
                _get_block_long_from_short_id(blockchain_id, short_id)
                for short_id in block_ids
            ]

        return block_ids
    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def get_blockchain_data(blockchain_id: str) -> str:
    """Create a zip file of all this blockchain's data, returning its path.

    Args:
        blockchain_id (str): the id or name of the blockchain to zip
    Returns:
        str: the path of the zip file created
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    request = blockchain_id.encode()

    _response = _send_request("get_blockchain_data", request)
    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        if response["success"]:
            return response["path"]

    except Exception:
        pass
    _error = _read_appcomterm_error_message(response)
    log.error(f"WAPI: {function_name()}: {str(_error)}")
    raise _error


def get_peers(blockchain_id: str) -> list[str]:
    """Get a list of IPFS IDs of the given blockchain's currently online nodes.

    Args:
        blockchain_id (str): the id or name of the blockchain to look up
    Returns:
        list[str]: the IPFS IDs of the blockchain's currently online nodes
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    request = blockchain_id.encode()

    _response = _send_request("get_peers", request)
    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        if response["success"]:
            return response["peers"]

    except Exception:
        pass
    _error = _read_appcomterm_error_message(response)
    log.error(f"WAPI: {function_name()}: {str(_error)}")
    raise _error


def create_invitation(
    blockchain_id: str, one_time: bool = True, shared: bool = False
) -> str:
    """Create a code which other nodes can use to join this blockchain.

    Args:
        blockchain_id (str): the id or name of the blockchain to create a
                        invitation for
        one_time (bool): (optional, default True) whether this code is valid
                        only for one use only instead of being reusable
        shared (bool): whether this invitation should be hosted by other
                        nodes who join this blockchain too, or just by this one
    Returns:
        str: an invitation code that can be used by other computers to join
                this blockchain
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    request = json.dumps(
        {
            "blockchain_id": blockchain_id,
            "one_time": one_time,
            "shared": shared,
        }
    ).encode()

    _response = _send_request("create_invitation", request)
    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        return response["invitation"]
    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def get_invitations(blockchain_id: str) -> list[str]:
    """Get the specified blockchain's active invitations.

    Args:
        blockchain_id (str): the id or name of the blockchain whose invitations
                                to look up
    Returns:
        list: the invitations of this blockchain
    """
    blockchain_id = get_blockchain_id(blockchain_id)

    # Sending request to Brenthy
    payload = blockchain_id.encode()

    # askig the blockchain to build and publish the block
    _response = _send_request("get_invitations", payload)

    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        if response["success"]:
            return response["invitations"]
        else:
            _error = _read_appcomterm_error_message(response)
            log.error(f"WAPI: {function_name()}: {str(_error)}")
            raise _error

    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def delete_invitation(blockchain_id: str, invitation: str) -> None:
    """Delete an invitation from the specified blockchain.

    Args:
        blockchain_id (str): the id or name of the blockchain to delete an
                            invitation from
        invitation (str): the invitation to delete
    """
    blockchain_id = get_blockchain_id(blockchain_id)
    request = json.dumps(
        {"blockchain_id": blockchain_id, "invitation": invitation}
    ).encode()

    _response = _send_request("delete_invitation", request)
    # Reading response from Brenthy
    try:
        response = json.loads(_response.decode())
        if not response["success"]:
            _error = _read_appcomterm_error_message(response)
            log.error(f"WAPI: {function_name()}: {str(_error)}")
            raise _error
    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def get_walytis_beta_version() -> tuple[int, int, int]:
    """Get the software version of the locally running Walytis node.

    Returns:
        tuple: the software version of the locally running Walytis_Beta node
    """
    # make request to Brenthy
    _response = _send_request("get_walytis_beta_version", bytearray([]))

    # read and process response from Brenthy
    try:
        response = json.loads(_response.decode())

        # handle unexpected response type
        if not (
            isinstance(response, dict)
            and (response.get("walytis_beta_core_version"), list)
        ):
            _error = _read_appcomterm_error_message(response)
            log.error(f"WAPI: {function_name()}: {str(_error)}")
            raise _error

        return tuple(response["walytis_beta_core_version"])

    except Exception:
        _error = _read_appcomterm_error_message(response)
        log.error(f"WAPI: {function_name()}: {str(_error)}")
        raise _error


def get_walytis_beta_version_string() -> str:
    """Get the software version of the locally running Walytis_Beta node.

    Returns:
        str: the software version of the locally running Walytis_Beta node
    """
    return version_to_string(get_walytis_beta_version())


def get_walytis_beta_api_version() -> tuple[int, int, int]:
    """Get the software version of the this walytis_beta_api library.

    Returns:
        tuple: the software version of the this walytis_beta_api library
    """
    return WALYTIS_BETA_API_VERSION


def get_walytis_beta_api_version_string() -> str:
    """Get the software version of the this walytis_beta_api library.

    Returns:
        str: the software version of the this walytis_beta_api library
    """
    return version_to_string(get_walytis_beta_api_version())


class BlocksListener:
    """Listen for a blockchain's new block events."""

    event_listener = None

    def __init__(
        self,
        blockchain_id: str,
        eventhandler: Callable[[Block, str], None] | Callable[[Block], None],
        topics: list[str] | None = None,
    ):
        """Call an eventhandler when the specified blockchain gets a new block.

        Args:
            blockchain_id (str): the id or name of the blockchain to listen on
            eventhandler (Callable[[Block, str], None]): eventhandler to call
                    when the blockchain gets a new block
            topics (list): the name of the topic to receive blocks from
        """
        blockchain_id = get_blockchain_id(blockchain_id)
        log.info(f"Walytis_BetaAPI: BlocksListener: {blockchain_id}")
        self.blockchain_id = blockchain_id
        self.eventhandler = eventhandler
        if isinstance(topics, str):
            topics = [topics]
        self.topics = topics

        self.event_listener = brenthy_api.EventListener(
            "Walytis_Beta", self._eventhandler, f"{blockchain_id}-NewBlocks"
        )

    def _eventhandler(self, data: dict, topic: str) -> None:
        """Handle new block messages, calling the user's eventhandler."""
        # decapsulate topic for documentation purposes
        blockchain_topic = topic.strip(f"{self.blockchain_id}-")

        block_id = string_to_bytes(data["block_id"])
        block = get_block(self.blockchain_id, block_id)
        log.info(
            "Walytis_BetaAPI: BlocksListener: got block: "
            f"{(self.topics, block.topics)}"
        )
        try:
            # if we aren't filtering by topics
            # or any of our topics match the topics of the block
            if not self.topics or list(
                set(self.topics).intersection(block.topics)
            ):
                self.eventhandler(block)
        except Exception as error:
            log.info(
                "Walytis_BetaAPI: BlocksListener: Error in eventhandler: "
                f"{type(error)} {error}"
            )

    def terminate(self) -> None:
        """Clean up all resources used by this object."""
        if self.event_listener:
            self.event_listener.terminate()

    def __del__(self) -> None:
        """Clean up all resources used by this object."""
        self.terminate()


def get_and_read_block(short_id: bytearray) -> Block:
    """Given a block's ID, download and verify it.

    Args:
        short_id (str): the ID of the block to get
    Returns:
        Block: an object representing the specified block, containing all its
                metadata and block content
    """
    try:
        ipfs_cid = decode_short_id(short_id)["ipfs_cid"]
        block_data = ipfs_api.read(ipfs_cid)
    except Exception:
        error = BlockNotFoundError()
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    try:
        block = read_block(block_data, ipfs_cid)
    except Exception as error:
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error
    while short_id[-1] == 0:
        short_id = short_id[:-1]
    if bytearray(block.short_id) != short_from_long_id(short_id):  # suspicious
        error_message = (
            "The decoded block's ID is not the same as the one we are looking "
            f"for.\nLooking for: {bytearray(short_id)}"
            f"\nGenerated from BlockData: {block.short_id}"
        )

        exception = BlockIntegrityError(error_message)
        log.error(f"WAPI: {function_name()}: {error_message}")
        raise exception
    return block


def read_block(block_data: bytearray, ipfs_cid: str) -> Block:
    """Read a block-file, generating a block object if it's valid.

    Args:
        block_data (bytearray): the raw data of the block to read.
        ipfs_cid (str): the IPFS content ID of the block
    Returns:
        Block: a Block object
    """
    # making a copy of the data to work with
    data = bytearray(block_data)
    # extract metadata block (separated from content by [0,0,0,0,0])
    # and splt it into is subcomponents separated by [0,0]
    content_separator = data.index(bytearray([0, 0, 0, 0, 0]))
    blockfile_header = data[:content_separator].split(bytearray([0, 0, 0, 0]))
    metadata = blockfile_header[0].split(bytearray([0, 0]))
    # log.important(data)
    # log.important(blockfile_header)
    # log.important(metadata)
    if len(blockfile_header) > 1:
        parents = blockfile_header[1].split(bytearray([0, 0, 0]))
    else:
        parents = []
        # log.important("Genesis block")
    # content sits between metadata and block_hash
    content = data[content_separator + 5:]

    blockchain_version = decode_version(metadata[0])
    creator_id = metadata[1]
    creation_time = decode_timestamp(metadata[2])

    topics = [topic.decode() for topic in metadata[3].split(bytearray([0]))]
    content_length = from_b255_no_0s(metadata[4])
    content_hash_algorithm = metadata[5].decode()
    content_hash = metadata[6]

    n_parents = from_b255_no_0s(metadata[7])
    parents_hash_algorithm = metadata[8].decode()
    parents_hash = metadata[9]

    # creating a new block object from the decoded block data
    block = Block.from_metadata(
        blockchain_version=blockchain_version,
        creator_id=creator_id,
        creation_time=creation_time,
        topics=topics,
        content_hash_algorithm=content_hash_algorithm,
        content_hash=content_hash,
        content=content,
        n_parents=n_parents,
        parents_hash_algorithm=parents_hash_algorithm,
        parents_hash=parents_hash,
        parents=parents,
        ipfs_cid=ipfs_cid,
        content_length=content_length,
        file_data=bytearray(block_data),
    )

    block.generate_id()

    # making sure the block's hash is correct
    if not block.check_integrity():
        error = BlockIntegrityError(
            "The received block had an incorrect hash. The block is "
            "considered corrupt or fraudulently manipulated."
        )
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    return block


def _read_appcomterm_error_message(
    data: dict | bytearray, default_error: BaseException | None = None
) -> BaseException:
    """Analyse a failed request reply, returning an appropriate Exception.

    Args:
        data (dict | bytearray): the response from the brenthy AppComTerm to
                                    analyse
        default_error(Exception): the exception to return if no error
                                    message/cause can be determined
    """
    if isinstance(data, dict):
        if "error" in data.keys():
            if data["error"] == NO_SUCH_BLOCKCHAIN_MESSAGE:
                if "blockchain_id" in data.keys():
                    return NoSuchBlockchainError(
                        blockchain_id=data["blockchain_id"]
                    )
                else:
                    return NoSuchBlockchainError()
            elif data["error"] == BLOCKCHAIN_EXISTS_MESSAGE:
                if "blockchain_name" in data.keys():
                    return BlockchainAlreadyExistsError(
                        blockchain_name=data["blockchain_name"]
                    )
                else:
                    return BlockchainAlreadyExistsError()
            elif data["error"] == NO_SUCH_INVITATION_MESSAGE:
                return NoSuchInvitationError()
            elif data["error"] == WALYTIS_BETA_ERROR_MESSAGE:
                return WalytisBugError(error_message=data["error"])
            if default_error:
                return default_error
            else:
                return WalytisReplyDecodeError(reply=str(data))
    if default_error:
        return default_error
    log.error(str(WalytisReplyDecodeError(reply=str(data))))
    return WalytisReplyDecodeError(reply=str(data))


def _send_request(function_name: str, payload: bytearray | bytes) -> bytearray:
    """Send a request to Walytis-Core.

    Args:
        function_name(str): the name of the function in walytis_api_terminal
                                which we want to call
        payload(bytearray): the data the function in walytis_beta_api_terminal
                                needs to process our request, its arguments

    Returns:
        bytearray: the reply from the function we called in
                                walytis_beta_api_terminal
    """
    request = (
        encode_version(WALYTIS_BETA_API_PROTOCOL_VERSION) + bytearray([0])
        + function_name.encode() + bytearray([0])
        + payload
    )
    reply = brenthy_api.send_request("Walytis_Beta", request)
    walytis_api_version = decode_version(reply[: reply.index(bytearray([0]))])
    reply = reply[reply.index(bytearray([0])) + 1:]
    return reply


def _get_block_long_from_short_id(blockchain_id: str, short_id: bytearray):
    """This function is needed for BACKWARDS COMPATIBILITY with older versions
    of Walytis_Beta Core."""
    return get_block(blockchain_id, short_id).long_id
