"""`walytis_beta_api` Blockchain class.

The herein contained Blockchain class isn't the code running the Walytis
blockchains themselves, it is merely a construct in `wlaytis_beta_api` for
providing the means to interact with a Walytis blockchain.

The real blockchain class for running blockchains in Walytis-Core is in:
Brenthy/blockchains/Walytis_Beta/walytis_beta.py
"""

import os
import shutil
from threading import Lock, Thread
from types import FunctionType

import appdirs
from brenthy_tools_beta import log
from brenthy_tools_beta.utils import (
    bytes_to_string,
    function_name,
    string_to_bytes,
)

from .block_model import Block
from .exceptions import (  # pylint: disable=unused-import
    BlockCreationError,
    BlockNotFoundError,
    NotSupposedToHappenError,
)
from .walytis_beta_interface import (
    WALYTIS_BETA,
    BlocksListener,
    create_block,
    create_blockchain,
    create_invitation,
    delete_blockchain,
    delete_invitation,
    get_block,
    get_blockchain_id,
    get_blockchain_name,
    get_invitations,
    get_latest_blocks,
    get_peers,
    join_blockchain,
)

brenthy_appdata_dir = os.path.join(appdirs.user_data_dir(), "Brenthy")
walytis_beta_appdata_dir = os.path.join(
    brenthy_appdata_dir, "Blockchains", WALYTIS_BETA
)

N_STARTUP_BLOCKS = (
    400  # how many of this blockchain's  blocks we should load on startup
)
# log.set_print_level("info")


class Blockchain:
    """Represents a running Walytis_Beta blockchain.

    Provides the means to interact with a Walytis blockchain.
    """

    def __init__(
        self,
        blockchain_id: str,
        block_received_handler: FunctionType | None = None,
        app_name: str = "",
        appdata_dir: str = "",
        auto_load_missed_blocks: bool = True,
        forget_appdata: bool = False,
        sequential_block_handling: bool = True,
    ):
        """Create an object to represent a Walytis blockchain.

        Args:
            blockchain_id (str): the id or name of the blockchain
            block_received_handler (FunctionType): function to be called every
                time a new block is received on this blockchain.
                This function should not have a long execution time because
                this class waits for its execution to finish before saving
                the received block in its list of processed blocks.
                If this eventhandler raises an exception, it will be called
                with the same block at a later stage.
                The same block is never passed to this handler twice, and
                no child block will ever be passed to this function before
                its parent block.
            auto_load_missed_blocks (bool): whether or not to automatically get
                and process the blocks received by the blockchain while
                this application was offline.
            app_name (str): the unique name of this application, to distinguish
                between different applications that use the same blockchain
                for appdata management
            appdata_dir (str): the directory in which to save data on which
                blocks this application has processed for this blockchain
            forget_appdata (bool): whether or not to ignore and overwrite any
                existing records of which blocks applications with the
                providede `app_name` have processed
            sequential_block_handling (bool): if True, the provided block-
                received handler will be executed on the main thread, and
                the handler will only be executed for the next block
                after the handler for the last block executes witout
                error.
                If set to False, the block-received handler will always be
                started on a new thread, meaning it is possible for
                multiple calls of the handler to be running in parallel
                for different blocks.
        """
        # declare attribute already to avoid error in destructor
        # if error occurs in constructor
        self._blocks_listener = None

        self.blockchain_id = get_blockchain_id(blockchain_id)
        self.name = get_blockchain_name(self.blockchain_id)
        self.app_name = app_name
        self.block_received_handler = block_received_handler
        self.block_ids: list[bytearray] = []

        if not isinstance(blockchain_id, str):
            error = TypeError(
                "The blockchain_id parameter must be of type string."
            )
            log.error(f"WAPI: {function_name()}: {str(error)}")
            raise error
        if appdata_dir and app_name:
            error = ValueError(
                "Don't pass both app_name and appdata_dir. "
                "You can pass one of them or none."
            )
            log.error(f"WAPI: {function_name()}: {str(error)}")
            raise error

        if not isinstance(app_name, str):
            error = TypeError("The app_name parameter must be of type string.")
            log.error(f"WAPI: {function_name()}: {str(error)}")
            raise error
        if not isinstance(appdata_dir, str):
            error = TypeError(
                "The appdata_dir parameter must be of type string."
            )
            log.error(f"WAPI: {function_name()}: {str(error)}")
            raise error
        if appdata_dir and not os.path.isdir(appdata_dir):
            _error = FileNotFoundError(
                "The appdata_dir parameter must be an exising directory."
            )
            log.error(f"WAPI: {function_name()}: {str(_error)}")
            raise _error

        self._blocklist_lock = Lock()
        self._terminate = False

        self.sequential_block_handling = sequential_block_handling
        self._blocks_listener = BlocksListener(
            self.blockchain_id, self._on_new_block_received
        )

        # if the user specified an appdata directory, use it
        if appdata_dir:
            self.appdata_dir = appdata_dir
        elif app_name:
            self.appdata_dir = os.path.join(
                walytis_beta_appdata_dir,
                self.blockchain_id,
                "Apps",
                self.app_name,
            )
            # if appdata path doesn't exist
            # and we're not being used by a temporary app
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
        else:
            self.appdata_dir = ""
        if forget_appdata and os.path.exists(self.appdata_dir):
            shutil.rmtree(self.appdata_dir)
        self._load_blocks_list()
        if auto_load_missed_blocks:
            self.load_missed_blocks(N_STARTUP_BLOCKS)

    def add_block(
        self, content: bytearray, topics: list[str] | str | None = None
    ) -> Block:
        """Add a new block to this blockchain.

        Args:
            content (bytearay): the content which the new block should have
            topics (list<str>): a list of topics this block belongs to
                    Topics allow blocks to be categorised by their application-
                    level function given the block ID only, without reading the
                    block content
        Returns:
            Block block: the newly created block
        """
        if type(content) not in [bytearray, bytes]:
            raise TypeError(
                "Content must be of type bytes or bytearray, not "
                f"{type(content)}"
            )
        self._blocklist_lock.acquire()

        if topics == []:
            topics = self.blockchain_id
        try:
            block = create_block(self.blockchain_id, content, topics=topics)
        except BlockCreationError as error:
            log.error(f"WAPI: {function_name()}: {str(error)}")
            self._blocklist_lock.release()
            raise error

        self.block_ids.append(block.short_id)
        self._save_blocks_list(True)

        self._blocklist_lock.release()

        return block

    def get_block(self, id: bytearray) -> Block:
        """Get a block object from this blockchain given its block ID.

        Args:
            id (bytearray): the id of the block to look up
                            or if int: the index of the block to look up
        Returns:
            Block: a Block object containing all the requested block's data
        """
        self._blocklist_lock.acquire()

        # if index is passed instead of block_id, get block_id from index
        if isinstance(id, int):
            try:
                id = self.block_ids[id]
            except IndexError:
                self._blocklist_lock.release()
                message = (
                    "Walytis_BetaAPI.Blockchain: Get Block from index: "
                    "Index out of range."
                )
                log.error(message)
                raise IndexError(message)

        for block_id in self.block_ids:
            if id == block_id:
                self._blocklist_lock.release()

                return get_block(self.blockchain_id, id)
                # metadata = decode_short_id(id)

                # block = DeserialiseBlock(ipfs_api.read(metadata["IPFS CID"]))
                # block = DeserialiseBlock(ipfs_api.read(metadata["IPFS CID"]))

                # self._blocklist_lock.release()

                # return block

        self._blocklist_lock.release()

        error = BlockNotFoundError(
            "This block isn't recorded (by brenthy_api.Blockchain) as being "
            "part of this blockchain."
        )
        log.error(f"WAPI: {function_name()}: {str(error)}")
        raise error

    def create_invitation(
        self, one_time: bool = True, shared: bool = False
    ) -> str:
        """Create a code which another node can use to join this blockchain.

        Args:
            one_time (bool): whether this code is non-reusable
            shared (bool): whether this invitation should be hosted by other
                    nodes who join this blockchain too, or just by this one
        Returns:
            str: a code that can be used by other nodes to join this blockchain
        """
        return create_invitation(
            self.blockchain_id, one_time=one_time, shared=shared
        )

    def delete_invitation(self, invitation: str) -> None:
        """Delete an invitation from this blockchain.

        Args:
            invitation (str): the invitation to delete
        """
        delete_invitation(self.blockchain_id, invitation)

    def get_invitations(self) -> list[str]:
        """Get a list of the invitations we're hositng for this blockchain.

        Returns:
            list: the invitations we're hosting for this blockchain,
                    as JSON strings
        """
        return get_invitations(self.blockchain_id)

    def get_peers(self) -> list[str]:
        """Get the IPFS peer IDs of blockchain nodes who are currently online.

        Returns:
            list[str]: a list of IPFS peer IDs of the currently connected nodes
        """
        return get_peers(self.blockchain_id)

    def _run_block_received_handler(self, block: Block) -> None:
        if not self.block_received_handler:
            return
        return_value = self.block_received_handler(block)
        if return_value is not None:
            raise ValueError(
                "block_received_handler must return None, as it's meaningful "
                "usage is reserved for future use"
            )

    def _on_new_block_received(
        self,
        block: Block,
        save_blocks_list: bool = True,
        already_locked: bool = False,
    ) -> None:
        """Handle a newly received block.

        Gets called when this blockchain received a new block. Saves the block
        in our block list and calls the appropriate user-defined eventhandlers.

        Args:
            block (Block): the newly received block
            save_blocks_list (bool): whether or not to save our updated list
                        of blocks to appdata
            already_locked (bool): whether or not we've already acquired the
                        lock for working with the blocks list
        """
        # if not already_locked:
        #     self._blocklist_lock.acquire()
        if block.short_id not in self.block_ids:
            for parent in block.parents:
                if parent not in self.block_ids:
                    self._on_new_block_received(
                        get_block(self.blockchain_id, parent),
                        save_blocks_list=save_blocks_list,
                        # already_locked=True
                        already_locked=already_locked,
                    )
            try:
                # call user's block_received_handler
                # only if the block isn't a genesis block
                if block.topics == ["genesis"]:
                    log.info("WAPI: Received Genesis Block!")
                elif self.block_received_handler:  # it's a normal block
                    if self.sequential_block_handling:
                        self._run_block_received_handler(block)
                    else:
                        Thread(
                            target=self._run_block_received_handler,
                            args=(block,),
                            name=f"WAPI-{self.name}-block_received_handler",
                        ).start()
                if not already_locked:
                    self._blocklist_lock.acquire()

                self.block_ids.append(block.short_id)
                if save_blocks_list:
                    self._save_blocks_list(already_locked=True)

                if not already_locked:
                    self._blocklist_lock.release()

            except Exception as e:
                log.error(f"WAPI: Blockchain._on_new_block_received: {e}")

    def _save_blocks_list(self, already_locked: bool = False) -> None:
        """Save our list of known/processed block IDs to an appdata file."""
        # don't save any appdata if we're being used by a temporary app
        if not self.appdata_dir:
            return
        if not already_locked:
            self._blocklist_lock.acquire()

        with open(
            os.path.join(self.appdata_dir, "blocks_list"), "w+"
        ) as filewriter:
            filewriter.writelines(
                [
                    bytes_to_string(block_id) + "\n"
                    for block_id in self.block_ids
                ]
            )
        if not already_locked:
            self._blocklist_lock.release()

    def load_missed_blocks(self, amount: int) -> None:
        """Get recent blocks.

        Ask the Blockchain for recent blocks on this topic that might have been
        received while this program was offline. Any of these missed blocks
        will trigger the self.block_received_handler event handler.

        Args:
            amount (int): the number of blocks to load
        """
        # self._blocklist_lock.acquire()
        log.info(amount)
        latest_blocks = get_latest_blocks(self.blockchain_id, amount=amount)
        if not latest_blocks:
            # self._blocklist_lock.release()
            error = NotSupposedToHappenError(
                "Got no latest blocks from blockchain. "
                "This is probably due to a bug in walytis_api."
            )
            log.error(f"WAPI: {function_name()}: {str(error)}")
            raise error
        count = 0
        for block_id in latest_blocks:
            if self._terminate:
                # self._blocklist_lock.release()
                return

            if block_id not in self.block_ids:
                try:
                    block = get_block(self.blockchain_id, block_id)
                    self._on_new_block_received(
                        block,
                        save_blocks_list=False,
                        # already_locked=True
                    )
                except Exception as e:
                    log.error(
                        f"Walytis_BetaAPI: Blockchain.load_missed_blocks: {e}"
                    )
            else:
                count += 1

        self._save_blocks_list(
            # already_locked=True
        )
        # self._blocklist_lock.release()

    def _load_blocks_list(self) -> None:
        """Load our list of known/processed block IDs from an appdata file."""
        if not self.appdata_dir:
            return

        self._blocklist_lock.acquire()

        if os.path.exists(os.path.join(self.appdata_dir, "blocks_list")):
            self.block_ids = []
            with open(
                os.path.join(self.appdata_dir, "blocks_list"), "r"
            ) as filereader:
                for line in filereader.readlines():
                    self.block_ids.append(string_to_bytes(line[:-1]))

        self._blocklist_lock.release()

    def terminate(self) -> None:
        """Clean up all resources this object uses."""
        self._terminate = True
        if self._blocks_listener:
            self._blocks_listener.terminate()

    def __del__(self) -> None:
        """Clean up all resources this object uses."""
        self.terminate()

    def delete(self) -> None:
        """Stop our participation in this blockchain.

        Locally deletes all data we have stored for it.
        """
        self.terminate()
        delete_blockchain(self.blockchain_id)

    @staticmethod
    def create(
        blockchain_name: str = "",
        block_received_handler: FunctionType | None = None,
        app_name: str = "",
        appdata_dir: str = "",
    ) -> 'Blockchain':
        """Create and run a new blockchain.

        Args:
            blockchain_name (str):
                blockchain's local name: a human-readable label
                to ease recognition when manually interacting with WalytisAPI.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.
            block_received_handler (FunctionType):
                A function to be called every
                time a new block is received on this blockchain.
                This function should not have a long execution time because
                this class waits for its execution to finish before saving
                the received block in its list of processed blocks.
                If this handler raises an exception, it will be called
                with the same block at a later stage.
                The same block is never passed to this handler twice, and
                no child block will ever be passed to this function before
                its parent block.
            app_name (str): the unique name of this application, to distinguish
                between different applications that use the same blockchain
                for appdata management
            appdata_dir (str): the directory in which to save data on which
                    blocks this application has processed for this blockchain

        Returns:
            Blockchain: a Blockchain object representing the created blockchain
        """
        blockchain_id = create_blockchain(blockchain_name=blockchain_name)
        return Blockchain(
            blockchain_id,
            block_received_handler=block_received_handler,
            app_name=app_name,
            appdata_dir=appdata_dir,
        )

    @staticmethod
    def join(
        invitation: str,
        blockchain_name: str = "",
        block_received_handler: FunctionType | None = None,
        app_name: str = "",
        appdata_dir: str = "",
    ) -> 'Blockchain':
        """Join a blockchain using an invitation generated by another node.

        Args:
            invitation (str): the invitation generated by a blockchain member
            blockchain_name (str):
                blockchain's local name: a human-readable label
                to ease recognition when manually interacting with WalytisAPI.
                Note: A blockchain's name only exists in the scope of a single
                node, meaning it is not guaranteed to be globally unique.
                Applications should use a blockchain's ID (attribute 'id') as
                its identifier, not the blockchain_name.
            block_received_handler (FunctionType):
                A function to be called every
                time a new block is received on this blockchain.
                This function should not have a long execution time because
                this class waits for its execution to finish before saving
                the received block in its list of processed blocks.
                If this handler raises an exception, it will be called
                with the same block at a later stage.
                The same block is never passed to this handler twice, and
                no child block will ever be passed to this function before
                its parent block.
            app_name (str): the unique name of this application, to distinguish
                between different applications that use the same blockchain
                for appdata management
            appdata_dir (str): the directory in which to save data on which
                    blocks this application has processed for this blockchain
        Returns:
            Blockchain: a Blockchain object representing the joined blockchain
        """
        blockchain_id = join_blockchain(
            invitation, blockchain_name=blockchain_name
        )
        return Blockchain(
            blockchain_id,
            block_received_handler=block_received_handler,
            app_name=app_name,
            appdata_dir=appdata_dir,
        )
