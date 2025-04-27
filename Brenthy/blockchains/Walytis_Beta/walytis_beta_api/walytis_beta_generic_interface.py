"""The machinery for communicating with Brenthy Core.

It contains functions that are a direct part of Walytis_Beta API and intended
for use by the Walytis_Beta API user (e.g. the create_blockchain() function),
but also functions that are used only by higher-level WalytisAPI constructs
such as BlocksListener class, which is not intended for use by the Walytis API
user, but is used by the blockchain_model.Blockchain class instead,
which is in turn intended for use by the Walytis_Beta API user.
"""

from __future__ import annotations


from __future__ import annotations
from typing import TypeVar, Type
import json
import os
import shutil
from datetime import datetime
from typing import Callable

from walytis_beta_tools._experimental.config import ipfs
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

from walytis_beta_tools.block_model import (
    Block,
    decode_short_id,  # pylint: disable=unused-import
    short_from_long_id
)
from walytis_beta_tools.exceptions import (
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

from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from typing import Callable, Type, TypeVar

from brenthy_tools_beta import log

from walytis_beta_tools.block_model import (
    Block,
)


# --- Blockchain IDs and Names ---

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class classproperty(Generic[T, R]):
    def __init__(self, func: Callable[[type[T]], R]) -> None:
        self.func = func

    def __get__(self, obj: Any, cls: type[T]) -> R:
        return self.func(cls)


class BaseBlocksListener(ABC):
    """Listen for a blockchain's new block events."""

    event_listener = None

    def __init__(
        self,
        blockchain_id: str,
        eventhandler: Callable[[Block], None],
        topics: list[str] | None = None,
    ):
        """Call an eventhandler when the specified blockchain gets a new block.

        Args:
            blockchain_id (str): the id or name of the blockchain to listen on
            eventhandler (Callable[[Block, str], None]): eventhandler to call
                    when the blockchain gets a new block
            topics (list): the name of the topic to receive blocks from
        """
        pass
    @abstractproperty
    def eventhandler(self)->Callable[[Block], None]:
        pass
    @abstractproperty
    def topics(self)->set[str]:
        pass
    @abstractproperty
    def blockchain_id(self)->str:
        pass
    def _on_event_received(self, data: dict,event_topics:set[str]) -> None:
        """Handle new block messages, calling the user's eventhandler."""
        # ensure event is relevant
        if f"{self.blockchain_id}-NewBlocks" not in event_topics:
            # log.debug(
            #     f"Discarding event with topics {event_topics} for "
            #     f"BlockListener for {self.blockchain_id}"
            # )
            return
        block_id = string_to_bytes(data["block_id"])
        block = self.get_block(block_id)
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

    @abstractmethod
    def get_block(self, block_id: bytearray) -> Block:
        """Get a block from the specified blokchain given its block ID.

        Args:
            blockchain_id (str): the id or name of the blockchain from which to get
                                    the block
            block_id (str): the id of the block
        Returns:
            Block: the Block object for the requested block
        """
        pass
        
    @abstractmethod
    def terminate(self) -> None:
        """Clean up all resources used by this object."""
        pass


TBlocksListener = TypeVar('TBlocksListener', bound=BaseBlocksListener)


class BaseWalytisBetaInterface(ABC):
    @abstractproperty
    @classproperty
    def BlocksListener(cls) -> Type[BaseBlocksListener]:
        pass

    @classmethod
    @abstractmethod
    def list_blockchains(cls, names_first: bool = False) -> list[tuple[str, str]]:
        """Get the IDs names of all the blockchains we have.

        Args:
            names_first: determines the order of the the tuple contents in the
                            return value. See Returns.

        Returns:
            list: A list of tuples of the names and IDs of all the Walytis_Beta
                    blockchains we have. Tuples are (id, name) by default,
                    but (name, id) if names_first == True
        """
        pass

    @classmethod
    def list_blockchain_names(cls,) -> list[str]:
        """Get the names of all the blockchains we have.

        Returns:
            list: A list of the names of all the Walytis_Beta blockchains we have.
        """
        return [name for id, name in cls.list_blockchains()]

    @classmethod
    def list_blockchain_ids(cls,) -> list[str]:
        """Get the ids of all the blockchains we have.

        Returns:
            list: A list of the names of all the Walytis_Beta blockchains we have.
        """
        return [id for id, name in cls.list_blockchains()]

    @classmethod
    def get_blockchain_id(cls, blockchain_name: str | bytearray) -> str:
        """Given a blockchain's name, returns its ID.

        If a blockchain's ID is given, it returns the ID.

        Args:
            blockchain_name (str): the name of the blockchain to look up
        Returns:
            str: the ID of the blockchain
        """
        blockchains = cls.list_blockchains()

        # if a blockchain id was passed
        if blockchain_name in [id for id, name in blockchains]:
            return blockchain_name
        for id, name in blockchains:
            if name == blockchain_name:
                return id
        error = NoSuchBlockchainError(blockchain_name=blockchain_name)
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    @classmethod
    def get_blockchain_name(cls, blockchain_id: str) -> str:
        """Given a blockchain's id, returns its name.

        If a blockchain's name is given, it returns the name.

        Args:
            blockchain_id (str): the id of the blockchain to look up
        Returns:
            str: the name of the blockchain
        """
        blockchains = cls.list_blockchains()

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

    @classmethod
    @abstractmethod
    def create_blockchain(cls, blockchain_name: str = "") -> str:
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
        pass

    @classmethod
    @abstractmethod
    def join_blockchain(cls, invitation: str, blockchain_name: str = "") -> str:
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
        pass

    @classmethod
    def join_blockchain_from_zip(cls,
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
            cid = ipfs.files.publish(tempdir)
        # if the appdata folder is a folder inside the zip file's
        elif os.path.exists(
            os.path.join(tempdir, blockchain_id, "KnownBlocksIndex")
        ):
            cid = ipfs.files.publish(os.path.join(tempdir, blockchain_id))
        else:
            error_message = (
                "The provided appdata zip file doesn't contain readable "
                "blockchain appdata"
            )
            log.error(error_message)
            raise JoinFailureError(error_message=error_message)
        shutil.rmtree(tempdir)
        log.debug(f"WAPI: {function_name()}: Ready to join blockchain...")

        return cls.join_blockchain_from_cid(blockchain_id, cid, blockchain_name)


    @classmethod
    @abstractmethod
    def join_blockchain_from_cid(cls,
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
        pass

    @classmethod
    @abstractmethod
    def delete_blockchain(cls, blockchain_id: str) -> None:
        """Delete the blockchain with the given id or name.

        Args:
            blockchain_id (str): the id or name of the blockchain to delete
        """
        pass

    @classmethod
    @abstractmethod
    def create_block(cls,
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
        pass

    @classmethod
    @abstractmethod
    def get_block(cls, blockchain_id: str, block_id: bytearray) -> Block:
        """Get a block from the specified blokchain given its block ID.

        Args:
            blockchain_id (str): the id or name of the blockchain from which to get
                                    the block
            block_id (str): the id of the block
        Returns:
            Block: the Block object for the requested block
        """
        pass

    @classmethod
    @abstractmethod
    def is_block_known(cls, blockchain_id: str, block_id: bytearray) -> bool:
        """Check whether or not the specified blockchain has the given block.

        Args:
            blockchain_id (str): the id or name of the blockchain to which the
                                    block to look up belongs
            block_id (bytearray): the block ID to look up in the block ID records
        Returns:
            bool: Whether the block is a known block
        """
        pass

    @classmethod
    @abstractmethod
    def get_latest_blocks(cls,
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
        pass

    @classmethod
    @abstractmethod
    def get_blockchain_data(cls, blockchain_id: str) -> str:
        """Create a zip file of all this blockchain's data, returning its path.

        Args:
            blockchain_id (str): the id or name of the blockchain to zip
        Returns:
            str: the path of the zip file created
        """
        pass

    @classmethod
    @abstractmethod
    def get_peers(cls, blockchain_id: str) -> list[str]:
        """Get a list of IPFS IDs of the given blockchain's currently online nodes.

        Args:
            blockchain_id (str): the id or name of the blockchain to look up
        Returns:
            list[str]: the IPFS IDs of the blockchain's currently online nodes
        """
        pass

    @classmethod
    @abstractmethod
    def create_invitation(cls,
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
        pass

    @classmethod
    @abstractmethod
    def get_invitations(cls, blockchain_id: str) -> list[str]:
        """Get the specified blockchain's active invitations.

        Args:
            blockchain_id (str): the id or name of the blockchain whose invitations
                                    to look up
        Returns:
            list: the invitations of this blockchain
        """
        pass

    @classmethod
    @abstractmethod
    def delete_invitation(cls, blockchain_id: str, invitation: str) -> None:
        """Delete an invitation from the specified blockchain.

        Args:
            blockchain_id (str): the id or name of the blockchain to delete an
                                invitation from
            invitation (str): the invitation to delete
        """
        pass

    @classmethod
    @abstractmethod
    def get_walytis_beta_version(cls, ) -> tuple[int, int, int]:
        """Get the software version of the locally running Walytis node.

        Returns:
            tuple: the software version of the locally running Walytis_Beta node
        """
        pass

    @classmethod
    def get_walytis_beta_version_string(cls,) -> str:
        """Get the software version of the locally running Walytis_Beta node.

        Returns:
            str: the software version of the locally running Walytis_Beta node
        """
        return version_to_string(cls.get_walytis_beta_version())

    @classmethod
    @abstractmethod
    def get_walytis_beta_api_version(cls, ) -> tuple[int, int, int]:
        """Get the software version of the this walytis_beta_api library.

        Returns:
            tuple: the software version of the this walytis_beta_api library
        """
        pass

    @classmethod
    def get_walytis_beta_api_version_string(cls,) -> str:
        """Get the software version of the this walytis_beta_api library.

        Returns:
            str: the software version of the this walytis_beta_api library
        """
        return version_to_string(cls.get_walytis_beta_api_version())

    @classmethod
    @abstractmethod
    def get_and_read_block(cls, short_id: bytearray) -> Block:
        """Given a block's ID, download and verify it.

        Args:
            short_id (str): the ID of the block to get
        Returns:
            Block: an object representing the specified block, containing all its
                    metadata and block content
        """
        pass

    @classmethod
    @abstractmethod
    def read_block(cls, block_data: bytearray, ipfs_cid: str) -> Block:
        """Read a block-file, generating a block object if it's valid.

        Args:
            block_data (bytearray): the raw data of the block to read.
            ipfs_cid (str): the IPFS content ID of the block
        Returns:
            Block: a Block object
        """
        pass
