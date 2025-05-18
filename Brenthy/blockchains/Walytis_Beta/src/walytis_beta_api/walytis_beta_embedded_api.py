"""The machinery for communicating with Brenthy Core.

It contains functions that are a direct part of Walytis_Beta API and intended
for use by the Walytis_Beta API user (e.g. the create_blockchain() function),
but also functions that are used only by higher-level WalytisAPI constructs
such as BlocksListener class, which is not intended for use by the Walytis API
user, but is used by the blockchain_model.Blockchain class instead,
which is in turn intended for use by the Walytis_Beta API user.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Callable, Type, TypeVar
from threading import Thread
from brenthy_tools_beta.utils import (
    make_directory_readable,
    make_file_readable,
)
from walytis_beta import walytis_beta
from walytis_beta_tools.block_model import (
    Block,
    decode_short_id,  # pylint: disable=unused-import
    short_from_long_id,
)
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
from walytis_beta_tools.versions import (
    WALYTIS_BETA_API_VERSION,
)
from walytis_beta_tools.block_model import short_from_long_id
from walytis_beta_tools.versions import (
    WALYTIS_BETA_CORE_VERSION,
)
from .walytis_beta_generic_interface import (
    BaseBlocksListener,
    BaseWalytisBetaInterface,
    classproperty,
)
from walytis_beta import walytis_beta_api_terminal


class _DirectBlocksListener(BaseBlocksListener):
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
        self._blockchain_id = WalytisBetaDirectInterface.get_blockchain_id(
            blockchain_id
        )
        self._eventhandler = eventhandler
        if isinstance(topics, str):
            topics = [topics]
        if topics:
            self._topics = set(topics)
        else:
            self._topics = set()
        walytis_beta_api_terminal.add_eventhandler(self._waly_event_received)
    def _waly_event_received(self, data: dict,topics:list[str]) -> None:
        Thread(
            target=self._on_event_received, args=(data, topics), 
            name=f"_DirectBlocksListener.eventhandler-{self.blockchain_id}"
        ).start()

        # self._on_event_received(data,set(topics))
    @property
    def blockchain_id(self)->str:
        return self._blockchain_id
    @property
    def topics(self)->set[str]:
        return self._topics
    @property
    def eventhandler(self) -> Callable[[Block], None]:
        return self._eventhandler
    def get_block(self, block_id: bytearray) -> Block:
        return WalytisBetaDirectInterface.get_block(self.blockchain_id, block_id)
    def terminate(self) -> None:
        """Clean up all resources used by this object."""
        pass


TBlocksListener = TypeVar('TBlocksListener', bound=BaseBlocksListener)


class WalytisBetaDirectInterface(BaseWalytisBetaInterface):
    @ classproperty
    def BlocksListener(cls) -> Type[DirectBlocksListener]:
        return _DirectBlocksListener

    @ classmethod
    def list_blockchains(cls, names_first: bool=False) -> list[tuple[str, str]]:
        """Get the IDs names of all the blockchains we have.

        Args:
            names_first: determines the order of the the tuple contents in the
                            return value. See Returns.

        Returns:
            list: A list of tuples of the names and IDs of all the Walytis_Beta
                    blockchains we have. Tuples are (id, name) by default,
                    but (name, id) if names_first == True
                    """
        
        if names_first:
            return [
            (blockchain.name, blockchain.blockchain_id)
            for blockchain in walytis_beta.blockchains
            
        ]
        else:
            return [
            (blockchain.blockchain_id, blockchain.name)
            for blockchain in walytis_beta.blockchains
        ]

    # --- Blockchain Lifecycle ---

    @ classmethod
    def create_blockchain(cls, blockchain_name: str="") -> str:
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
        blockchain = walytis_beta.create_blockchain(blockchain_name)
        if not blockchain:
            raise BlockchainAlreadyExistsError()
        return blockchain.blockchain_id

    @ classmethod
    def join_blockchain(cls, invitation: str, blockchain_name: str="") -> str:
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
        blockchain = walytis_beta.join_blockchain(
            invitation, blockchain_name=blockchain_name
        )
        if not blockchain:
            raise JoinFailureError()
        return blockchain.blockchain_id

    @ classmethod
    def join_blockchain_from_cid(cls,
                                 blockchain_id: str, blockchain_data_cid: str, blockchain_name: str=""
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
        blockchain = walytis_beta.join_blockchain_from_cid(
            blockchain_id, blockchain_data_cid, blockchain_name=blockchain_name
        )
        if not blockchain:
            raise JoinFailureError()
        return blockchain.blockchain_id

    @ classmethod
    def delete_blockchain(cls, blockchain_id: str) -> None:
        """Delete the blockchain with the given id or name.

        Args:
            blockchain_id (str): the id or name of the blockchain to delete
        """
        blockchain_id=cls.get_blockchain_id(blockchain_id)
        walytis_beta.delete_blockchain(blockchain_id)

    @ classmethod
    def create_block(cls,
                     blockchain_id: str,
                     content: bytearray | bytes,
                     topics: list[str] | str | None=None
                     ) -> Block:
        """Create a block with the given content on the specified blockchain.

        Args:
            blockchain_id (str): the id or name of the blockchain to create a block
            content (bytearray): the content to store on the blockchain
            topics (list): user's metadata to encode in the block's ID
        Returns:
            Block: the newly created block
        """
        blockchain = cls._get_blockchain(blockchain_id)
        if topics is None:
            topics = []
        elif isinstance(topics, str):
            topics = [topics]
        block = blockchain.create_block(content, topics)
        return block

    @ classmethod
    def get_block(cls, blockchain_id: str, block_id: bytearray) -> Block:
        """Get a block from the specified blokchain given its block ID.

        Args:
            blockchain_id (str): the id or name of the blockchain from which to get
                                    the block
            block_id (str): the id of the block
        Returns:
            Block: the Block object for the requested block
        """
        blockchain = cls._get_blockchain(blockchain_id)
        if blockchain.is_block_known(block_id):
            ipfs_cid = decode_short_id(block_id)["ipfs_cid"]
            data_file = blockchain.get_block_datafile_path(block_id)
            with open(data_file, "rb") as file:
                block_data = file.read()
            block = blockchain.read_block(block_data, ipfs_cid, live=False)
        else:
            block = blockchain.download_and_process_block(block_id)
        if not block:
            raise BlockNotFoundError()
        return block

    @ classmethod
    def is_block_known(cls, blockchain_id: str, block_id: bytearray) -> bool:
        """Check whether or not the specified blockchain has the given block.

        Args:
            blockchain_id (str): the id or name of the blockchain to which the
                                    block to look up belongs
            block_id (bytearray): the block ID to look up in the block ID records
        Returns:
            bool: Whether the block is a known block
        """
        blockchain = cls._get_blockchain(blockchain_id)
        return blockchain.is_block_known(block_id)

    @ classmethod
    def get_latest_blocks(cls,
                          blockchain_id: str,
                          amount: int | None=None,
                          since_date: datetime | None=None,
                          topics: list[str] | None=None,
                          long_ids: bool=False,  # defaults to False for backwards-compatibility
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
        blockchain = cls._get_blockchain(blockchain_id)
        block_ids = blockchain.load_latest_block_ids(
            amount, since_date, topics
        )
        if long_ids:
            return block_ids
        else:
            return [
                short_from_long_id(block_id) for block_id in block_ids
            ]

    @ classmethod
    def get_blockchain_data(cls, blockchain_id: str) -> str:
        """Create a zip file of all this blockchain's data, returning its path.

        Args:
            blockchain_id (str): the id or name of the blockchain to zip
        Returns:
            str: the path of the zip file created
        """
        blockchain = cls._get_blockchain(blockchain_id)
        result = blockchain.zip_appdata()
        make_file_readable(result)
        make_directory_readable(os.path.dirname(result))
        return result

    @ classmethod
    def get_peers(cls, blockchain_id: str) -> list[str]:
        """Get a list of IPFS IDs of the given blockchain's currently online nodes.

        Args:
            blockchain_id (str): the id or name of the blockchain to look up
        Returns:
            list[str]: the IPFS IDs of the blockchain's currently online nodes
        """
        blockchain = cls._get_blockchain(blockchain_id)

        return blockchain.get_peers()

    @ classmethod
    def create_invitation(cls,
                          blockchain_id: str, one_time: bool=True, shared: bool=False
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
        blockchain = cls._get_blockchain(blockchain_id)
        return blockchain.create_invitation(
            one_time=one_time, shared=shared
        )

    @ classmethod
    def get_invitations(cls, blockchain_id: str) -> list[str]:
        """Get the specified blockchain's active invitations.

        Args:
            blockchain_id (str): the id or name of the blockchain whose invitations
                                    to look up
        Returns:
            list: the invitations of this blockchain
        """
        blockchain = cls._get_blockchain(blockchain_id)
        return blockchain.invitations

    @ classmethod
    def delete_invitation(cls, blockchain_id: str, invitation: str) -> None:
        """Delete an invitation from the specified blockchain.

        Args:
            blockchain_id (str): the id or name of the blockchain to delete an
                                invitation from
            invitation (str): the invitation to delete
        """
        blockchain = cls._get_blockchain(blockchain_id)
        blockchain.delete_invitation(invitation)

    @ classmethod
    def get_walytis_beta_version(cls, ) -> tuple[int, int, int]:
        """Get the software version of the locally running Walytis node.

        Returns:
            tuple: the software version of the locally running Walytis_Beta node
        """
        return WALYTIS_BETA_CORE_VERSION

    @ classmethod
    def get_walytis_beta_api_version(cls, ) -> tuple[int, int, int]:
        """Get the software version of the this walytis_beta_api library.

        Returns:
            tuple: the software version of the this walytis_beta_api library
        """
        return WALYTIS_BETA_API_VERSION
    @ classmethod
    def _get_blockchain(cls, blockchain_id: str) -> walytis_beta.Blockchain:
        blockchain_id = cls.get_blockchain_id(blockchain_id)
        blockchain = walytis_beta.get_blockchain(blockchain_id)
        if blockchain:
            return blockchain
        raise NoSuchBlockchainError(blockchain_id=blockchain_id)
    @ classmethod
    def get_and_read_block(cls, short_id: bytearray) -> Block:
        """Given a block's ID, download and verify it.

        Args:
            short_id (str): the ID of the block to get
        Returns:
            Block: an object representing the specified block, containing all its
                    metadata and block content
        """
        pass

    @ classmethod
    def read_block(cls, block_data: bytearray, ipfs_cid: str) -> Block:
        """Read a block-file, generating a block object if it's valid.

        Args:
            block_data (bytearray): the raw data of the block to read.
            ipfs_cid (str): the IPFS content ID of the block
        Returns:
            Block: a Block object
        """
        pass
