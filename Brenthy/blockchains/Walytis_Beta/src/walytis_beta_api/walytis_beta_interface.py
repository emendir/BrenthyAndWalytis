"""The machinery for communicating with Brenthy Core.

It contains functions that are a direct part of Walytis_Beta API and intended
for use by the Walytis_Beta API user (e.g. the create_blockchain() function),
but also functions that are used only by higher-level WalytisAPI constructs
such as BlocksListener class, which is not intended for use by the Walytis API
user, but is used by the blockchain_model.Blockchain class instead,
which is in turn intended for use by the Walytis_Beta API user.
"""

from enum import Enum
import os
from .walytis_beta_generic_interface import BaseWalytisBetaInterface
from datetime import datetime

from brenthy_tools_beta import log

from walytis_beta_tools.block_model import Block

from walytis_beta_tools.exceptions import (
    BlockchainAlreadyExistsError,  # noqa
    BlockIntegrityError,  # noqa
    BlockNotFoundError,  # noqa
    JoinFailureError,  # noqa
    NoSuchBlockchainError,  # noqa
    NoSuchInvitationError,  # noqa
    WalytisBugError,  # noqa
    WalytisReplyDecodeError,  # noqa
)
from walytis_beta_tools.exceptions import (
    NO_SUCH_BLOCKCHAIN_MESSAGE,
    NO_SUCH_INVITATION_MESSAGE,
    BLOCK_NOT_FOUND,
    WALYTIS_BETA_ERROR_MESSAGE,
    BLOCKCHAIN_EXISTS_MESSAGE,
)
# storing this blockchain's name so that we don't missspell it
WALYTIS_BETA = "Walytis_Beta"


# --------------Settings ---------------------------
log.PRINT_DEBUG = False




_waly: BaseWalytisBetaInterface


class WalytisBetaApiTypes(Enum):
    WALYTIS_BETA_BRENTHY_API = 0
    WALYTIS_BETA_DIRECT_API = 1

WalytisBetaApiTypes.WALYTIS_BETA_BRENTHY_API.name
_WALYTIS_BETA_API_TYPE = os.getenv("WALYTIS_BETA_API_TYPE")

if not _WALYTIS_BETA_API_TYPE:
    # if environment variable wasn't set, use default
    WALYTIS_BETA_API_TYPE = WalytisBetaApiTypes.WALYTIS_BETA_BRENTHY_API
else:
    type_match = None
    for wapi_type in WalytisBetaApiTypes:
        if _WALYTIS_BETA_API_TYPE == wapi_type.name:
            type_match = wapi_type
    if not type_match:
        raise Exception(
            "Invalid value for environment variable WALYTIS_BETA_API_TYPE "
            f"'{_WALYTIS_BETA_API_TYPE}'\n"
            f"Valid values are: {[member.name for member in WalytisBetaApiTypes]}"
        )
    WALYTIS_BETA_API_TYPE = type_match


match WALYTIS_BETA_API_TYPE:
    case WalytisBetaApiTypes.WALYTIS_BETA_BRENTHY_API:
        from .walytis_beta_brenthy_api import WalytisBetaNetApi
        _waly = WalytisBetaNetApi()
    case WalytisBetaApiTypes.WALYTIS_BETA_DIRECT_API:
        from .walytis_beta_embedded_api import WalytisBetaDirectInterface
        _waly = WalytisBetaDirectInterface()
    case _:
        raise WalytisBugError(
            "walytis_beta_interface: Didn't take into account how to process "
            f"WALYTIS_BETA_API_TYPE {WALYTIS_BETA_API_TYPE}"
        )
log.info(WALYTIS_BETA_API_TYPE)
BlocksListener = _waly.BlocksListener


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
    return _waly.list_blockchains(names_first=names_first)


def list_blockchain_names() -> list[str]:
    """Get the names of all the blockchains we have.

    Returns:
        list: A list of the names of all the Walytis_Beta blockchains we have.
    """
    return _waly.list_blockchain_names()


def list_blockchain_ids() -> list[str]:
    """Get the ids of all the blockchains we have.

    Returns:
        list: A list of the names of all the Walytis_Beta blockchains we have.
    """
    return _waly.list_blockchain_ids()


def get_blockchain_id(blockchain_name: str | bytearray) -> str:
    """Given a blockchain's name, returns its ID.

    If a blockchain's ID is given, it returns the ID.

    Args:
        blockchain_name (str): the name of the blockchain to look up
    Returns:
        str: the ID of the blockchain
    """
    return _waly.get_blockchain_id(blockchain_name)


def get_blockchain_name(blockchain_id: str) -> str:
    """Given a blockchain's id, returns its name.

    If a blockchain's name is given, it returns the name.

    Args:
        blockchain_id (str): the id of the blockchain to look up
    Returns:
        str: the name of the blockchain
    """
    return _waly.get_blockchain_name(blockchain_id)


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
    return _waly.create_blockchain(blockchain_name)


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
    return _waly.join_blockchain(invitation, blockchain_name)


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
    return _waly.join_blockchain_from_zip(
        blockchain_id, blockchain_data_path, blockchain_name
    )


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
    return _waly.join_blockchain_from_cid(
        blockchain_id, blockchain_data_cid, blockchain_name
    )


def delete_blockchain(blockchain_id: str) -> None:
    """Delete the blockchain with the given id or name.

    Args:
        blockchain_id (str): the id or name of the blockchain to delete
    """
    return _waly.delete_blockchain(blockchain_id)


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
    return _waly.create_block(
        blockchain_id,
        content,
        topics,
    )


def get_block(blockchain_id: str, block_id: bytearray) -> Block:
    """Get a block from the specified blokchain given its block ID.

    Args:
        blockchain_id (str): the id or name of the blockchain from which to get
                                the block
        block_id (str): the id of the block
    Returns:
        Block: the Block object for the requested block
    """
    return _waly.get_block(blockchain_id, block_id)


def is_block_known(blockchain_id: str, block_id: bytearray) -> bool:
    """Check whether or not the specified blockchain has the given block.

    Args:
        blockchain_id (str): the id or name of the blockchain to which the
                                block to look up belongs
        block_id (bytearray): the block ID to look up in the block ID records
    Returns:
        bool: Whether the block is a known block
    """
    return _waly.is_block_known(blockchain_id, block_id)


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
    return _waly.get_latest_blocks(
        blockchain_id=blockchain_id,
        amount=amount,
        since_date=since_date,
        topics=topics,
        long_ids=long_ids,
    )


def get_blockchain_data(blockchain_id: str) -> str:
    """Create a zip file of all this blockchain's data, returning its path.

    Args:
        blockchain_id (str): the id or name of the blockchain to zip
    Returns:
        str: the path of the zip file created
    """
    return _waly. get_blockchain_data(blockchain_id)


def get_peers(blockchain_id: str) -> list[str]:
    """Get a list of IPFS IDs of the given blockchain's currently online nodes.

    Args:
        blockchain_id (str): the id or name of the blockchain to look up
    Returns:
        list[str]: the IPFS IDs of the blockchain's currently online nodes
    """
    return _waly.get_peers(blockchain_id)


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
    return _waly.create_invitation(
        blockchain_id=blockchain_id, one_time=one_time, shared=shared
    )


def get_invitations(blockchain_id: str) -> list[str]:
    """Get the specified blockchain's active invitations.

    Args:
        blockchain_id (str): the id or name of the blockchain whose invitations
                                to look up
    Returns:
        list: the invitations of this blockchain
    """
    return _waly.get_invitations(blockchain_id)


def delete_invitation(blockchain_id: str, invitation: str) -> None:
    """Delete an invitation from the specified blockchain.

    Args:
        blockchain_id (str): the id or name of the blockchain to delete an
                            invitation from
        invitation (str): the invitation to delete
    """
    return _waly.delete_invitation(blockchain_id, invitation)


def get_walytis_beta_version() -> tuple[int, int, int]:
    """Get the software version of the locally running Walytis node.

    Returns:
        tuple: the software version of the locally running Walytis_Beta node
    """
    return _waly.get_walytis_beta_version()


def get_walytis_beta_version_string() -> str:
    """Get the software version of the locally running Walytis_Beta node.

    Returns:
        str: the software version of the locally running Walytis_Beta node
    """
    return _waly.get_walytis_beta_version_string()


def get_walytis_beta_api_version() -> tuple[int, int, int]:
    """Get the software version of the this walytis_beta_api library.

    Returns:
        tuple: the software version of the this walytis_beta_api library
    """
    return _waly.get_walytis_beta_api_version()


def get_walytis_beta_api_version_string() -> str:
    """Get the software version of the this walytis_beta_api library.

    Returns:
        str: the software version of the this walytis_beta_api library
    """
    return _waly.get_walytis_beta_api_version_string()


def get_and_read_block(short_id: bytearray) -> Block:
    """Given a block's ID, download and verify it.

    Args:
        short_id (str): the ID of the block to get
    Returns:
        Block: an object representing the specified block, containing all its
                metadata and block content
    """
    return _waly.get_and_read_block(short_id)


def read_block(block_data: bytearray, ipfs_cid: str) -> Block:
    """Read a block-file, generating a block object if it's valid.

    Args:
        block_data (bytearray): the raw data of the block to read.
        ipfs_cid (str): the IPFS content ID of the block
    Returns:
        Block: a Block object
    """
    return _waly.read_block(block_data, ipfs_cid)
