"""Networking machinery for the Walytis Blockchain (except joining)."""

from ipfs_tk_generics import IpfsClient
import json
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from random import randint
from threading import Lock
from ipfs_node import IpfsNode
from ipfs_tk_generics import IpfsClient
from ipfs_tk_peer_monitor import PeerMonitor

from .exceptions import BlockchainTerminatedError

if True:
    # pylint: disable=import-error
    from brenthy_tools_beta import log
    from brenthy_tools_beta.utils import bytes_to_string, string_to_bytes
    
    from walytis_beta_tools._experimental.config import ipfs


    # walytis_beta_tools must be loaded only after IPFS is initialised
    from walytis_beta_tools.block_model import decode_short_id

STARTUP_BLOCKLISTENER_PATIENCE = 10  # seconds
RUNTIME_BLOCKLISTENER_PATIENCE = 20  # seconds
PM_FILE_WRITE_INTERVALL_SEC = 20
# estimation of the latency in block-message composition, pubsub-transmission
# and reception-processing  (prefer overestimate, NON-ZERO)
estimated_pubsub_latency_sec = 10  # TODO: measure pubsub latency

# at what intervall should we check the number of pubsub-connected peers
PUBSUB_PEERS_CHECK_INTERVALL_S = 100


class Networking(ABC):
    """The Walytis blockchain's networking machinery."""

    lastcoms_time = datetime.utcnow()
    pubsub_topic = ""
    # variable for keeping track of the newest of LatestBlockRequests replies
    __shared_leaf_blocks: dict[str, datetime] = {}
    __lslb_lock = (
        Lock()
    )  # lock to regulate access to self.__shared_leaf_blocks

    # defined in class Blockchain:
    blockchain_id: str
    name: str
    current_endblocks: list[bytearray]
    _terminate: bool

    # defined in walytis_beta_appdata
    ipfs_peers_path = ""
    ipfs: IpfsClient

    def __init__(self):
        """Initialise core networking machinery."""

        try:
            self.peer_monitor = PeerMonitor(ipfs, self.ipfs_peers_path)
        except json.decoder.JSONDecodeError:
            os.remove(self.ipfs_peers_path)
            self.peer_monitor = PeerMonitor(ipfs, self.ipfs_peers_path)
        self.peer_monitor.file_write_interval_sec = PM_FILE_WRITE_INTERVALL_SEC
        # initialise pubsub peer count tracking
        self._pubsub_peers = 0
        self._last_pubsub_peers_check = datetime.utcnow() - timedelta(
            seconds=PUBSUB_PEERS_CHECK_INTERVALL_S + 1
        )
        self.ipfs_peer_id = ipfs.peer_id

    def listen_for_blocks(self) -> None:
        """Start listening for new blocks on this blockchain."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        self.pubsub_listener = ipfs.pubsub.subscribe(
            self.blockchain_id, self.pubsub_message_handler
        )
        log.info(f"Created PubSub listener for {self.name}")

    def pubsub_message_handler(self, pubsub_packet: dict) -> None:
        """Handle a pubsub message on the channel for new blocks comms."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        if self._terminate:
            return

        try:
            data = json.loads(pubsub_packet["data"].decode())
            sender_id = pubsub_packet["senderID"]
        except Exception as e:
            log.error(e)
            raise TypeError(
                f"Pubsub message handler received unexpected type "
                f"{type(pubsub_packet)}"
            )
        message: str = data["message"]
        if not sender_id == self.ipfs_peer_id:
            self.peer_monitor.register_contact_event(sender_id)
        if message == "New block!":
            # log.info(f"PubSub: Received data for new block on {self.name}.")
            self.lastcoms_time = datetime.utcnow()
            self.update_shared_leaf_blocks([data["block_id"]])
            self.new_block_published(string_to_bytes(data["block_id"]))

        elif message == "Leaf blocks:":
            # log.info(f"PubSub: Received leaf blocks broadcast on {self.name}.")
            self.lastcoms_time = datetime.utcnow()
            # leaf_blocks = [
            #     string_to_bytes(block_id) for block_id in data["leaf_blocks"]
            # ]
            leaf_blocks = data["leaf_blocks"]
            self.update_shared_leaf_blocks(leaf_blocks)
            for block_id_str in leaf_blocks:
                block_id = string_to_bytes(block_id_str)
                # download and process block if we don't know it yet
                if not self.is_block_known(block_id):
                    self.new_block_published(block_id)

            # Wait random duration
            # to prevent all nodes from answering at once:
            try:
                self.wait_seconds(self.network_random_duration())
            except BlockchainTerminatedError:
                return

            # reply with our latest block
            # (if nobody else has published a newer on in the meantime)
            self.check_and_publish_leaf_blocks()

    def update_shared_leaf_blocks(
        self, leaf_blocks: list[str], already_locked: bool = False
    ) -> None:
        """Add the provided block IDs to our list of shared leaf-blocks."""
        now = datetime.utcnow()
        if not already_locked:
            self.__lslb_lock.acquire()
        # update list with newly broadcast blocks
        for block_id_str in leaf_blocks:
            if block_id_str in self.__shared_leaf_blocks.keys():
                self.__shared_leaf_blocks[block_id_str] = now
            else:
                self.__shared_leaf_blocks.update({block_id_str: now})

        # remove older entries in list
        for block_id_str in list(self.__shared_leaf_blocks.keys()):
            entry_age = (
                now - self.__shared_leaf_blocks[block_id_str]
            ).total_seconds()
            if entry_age > RUNTIME_BLOCKLISTENER_PATIENCE:
                self.__shared_leaf_blocks.pop(block_id_str)

        if not already_locked:
            self.__lslb_lock.release()

    def check_and_publish_leaf_blocks(self) -> None:
        """Publish a latestblock message if the last message's were older."""
        leaf_blocks = [
            bytes_to_string(block_id) for block_id in self.current_endblocks
        ]

        # if this blockchain is up and running properly yet, exit
        if not leaf_blocks:
            return

        self.__lslb_lock.acquire()

        # clean up outdated entries
        self.update_shared_leaf_blocks([], already_locked=True)

        broadcast = False
        for block_id_str in leaf_blocks:
            if block_id_str not in self.__shared_leaf_blocks.keys():
                broadcast = True
                break

        if broadcast:
            data = json.dumps(
                {"message": "Leaf blocks:", "leaf_blocks": leaf_blocks}
            ).encode()
            try:
                ipfs.pubsub.publish(self.blockchain_id, data)
            except Exception as e:
                log.error(e)
        self.update_shared_leaf_blocks(leaf_blocks, already_locked=True)
        self.__lslb_lock.release()

    def leaf_blocks_broadcaster(
        self,
    ) -> None:
        """Broadcast our leaf blocks whenever the pubsub channel gets quiet."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        waiting_duration = STARTUP_BLOCKLISTENER_PATIENCE
        self.wait_seconds(waiting_duration)

        while not self._terminate:
            time_since_last_coms = None
            if self.lastcoms_time:
                time_since_last_coms = (
                    datetime.utcnow() - self.lastcoms_time
                ).total_seconds()
            if (
                not time_since_last_coms
                or time_since_last_coms >= waiting_duration
            ):
                # data = json.dumps({
                #     "message": "What's the latest block?"
                # }).encode()
                # ipfs.pubsub.publish(self.blockchain_id, data)
                self.check_and_publish_leaf_blocks()

            waiting_duration = (
                RUNTIME_BLOCKLISTENER_PATIENCE + self.network_random_duration()
            )
            self.wait_seconds(waiting_duration)

    def get_pubsub_peers(self):
        if (
            (datetime.utcnow() - self._last_pubsub_peers_check).total_seconds()
            > PUBSUB_PEERS_CHECK_INTERVALL_S
        ):
            self._pubsub_peers = ipfs.pubsub.list_peers(self.blockchain_id)
            self._last_pubsub_peers_check = datetime.utcnow()
        return self._pubsub_peers

    def network_random_duration(self) -> int:
        """Get random waiting duration for simultaneous broadacast avoidance.

        Use this to prevent all nodes from broadcasting at once.
        The duration is proportional to the number of connected Walytis nodes
        and the estimated network latency.
        """
        # the number of Brenthy nodes we are connected to on pubsub
        return randint(
            0, len(self.get_pubsub_peers()) * estimated_pubsub_latency_sec
        )

    def wait_seconds(self, seconds: int) -> bool:
        """Wait for the given duration, breaking if we're shutting down.

        Args:
            seconds (int): duration to wait for
        Returns:
            bool: whether or not this blockchain is still running
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        for i in range(seconds):
            time.sleep(1)
            if self._terminate:
                return False
        return True

    def get_newest_block_id(self) -> bytearray | None:
        """Return the short_id of the newest block we have."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        if not self.current_endblocks:
            return None
        latest_time = decode_short_id(self.current_endblocks[0])[
            "creation_time"
        ]
        latest_block = self.current_endblocks[0]
        for short_id in self.current_endblocks:
            if latest_time < decode_short_id(short_id)["creation_time"]:
                latest_time = decode_short_id(short_id)["creation_time"]
                latest_block = short_id
        return latest_block

    def get_peers(self) -> list[str]:
        """Get IPFS peer IDs of nodes who are currently online."""
        # get peers who are currently online
        pubsub_peers = self.get_pubsub_peers()

        # get peer IDs and date of last contact of peers from whome we have
        # received messages from recently who are currently online
        contacted_peers = [
            (peer.peer_id(), peer.last_seen())
            for peer in self.peer_monitor.peers()
            if peer.peer_id() in pubsub_peers
        ]
        # sort by date, newest first
        contacted_peers.sort(key=lambda x: x[1], reverse=True)

        peers = [peer_id for peer_id, last_seen in contacted_peers]

        # get peers we are connected to on the pubsub channel
        # from whom we haven't heard any messages yet
        for peer in pubsub_peers:
            if peer not in peers:
                peers.append(peer)
        return peers

    @abstractmethod  # defined in BlockRecords
    def is_block_known(self, block_id: bytearray) -> bool:
        """Check if the given block ID exists in our block records."""
        pass

    @abstractmethod  # defined in Blockchain
    def new_block_published(self, short_id: bytearray) -> None:
        """Eventhandler for when a notification of a new block is received."""
        pass

    @abstractmethod  # defined in Blockchain
    def check_alive(self) -> None:
        """Raise an exception if this blockchain is not running."""
        pass

    def terminate_networking(self) -> None:
        """Shut down communications, cleaning up resources."""
        self.pubsub_listener.terminate(True)
        self.peer_monitor.terminate(True)
        log.info(f"Walytis_Beta: {self.name}: Shut down networking.")
