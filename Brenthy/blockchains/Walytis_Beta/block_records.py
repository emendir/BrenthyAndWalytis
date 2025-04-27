"""Machinery for recording and looking up block IDs.

Storing all the long IDs of all the blocks ever created in one file
would be rather inefficient because that file would grow to several gigabytes.
Therefore, this index system creates new files for recording new block IDs
when the older files become too large.

ID recording format: long_id + 000000
"""

import os

from .networking import ipfs

if True:
    # pylint: disable=import-error
    from brenthy_tools_beta import log
    from brenthy_tools_beta.utils import (
        from_b255_no_0s,
        string_to_time,
        time_to_string,
        to_b255_no_0s,
    )

import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from threading import Event, Lock

from walytis_beta_tools.exceptions import (
    InvalidBlockIdError,
    NotSupposedToHappenError,
)
from walytis_beta_tools.block_model import (
    Block,
    decode_long_id,
    decode_short_id,
    short_from_long_id,
)

MAX_BLOCKS_CACHE = 100  # maximum size of block cache


class BlockRecords(ABC):
    """Class for managing a blockchain's block records.

    This class is inherited by the Blockchain class.
    """

    # @abstractproperty
    name = ""

    # defined in walytis_beta_appdata
    received_blocks_dir = ""
    known_blocks_index_dir = ""
    block_record_initialised = Event()

    def __init__(self):
        """Initialise block records management."""
        self.max_num_blocks_per_file = 1000
        self.index_dir = ""

        # elements: Tuple(index_file_name, index_file_creation_time),
        # sorted byt the index_file's starting datetime (its name)
        self.index_files_times = []
        self.index_bookmarks = list([tuple((bytearray([0, 0]), 0))])
        self.index_lock = Lock()
        self.number_of_known_ids = None
        # how many blocks are recorded in the current index file
        self.current_file_length = 0

        self.block_record_initialised = Event()

        self.index_dir = self.known_blocks_index_dir
        self.create_index()
        self.ensure_ipfs_pinned()

        self._genesis_block_id = None

        # a list of the most recently used block IDs
        # so that they don't have to be looked up in the index files
        self.block_id_cache = []

        self.block_record_initialised.set()

    def check_new_block(self, block: Block) -> bool:
        """Check if a block is known, if not record it in the block records.

        Args:
            block (Block): the new block to check
        Returns:
            bool: whether or not the block is already known
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        self.block_record_initialised.wait()

        long_id = block.long_id
        decode_long_id(long_id)

        # making sure there aren't any separator [0]s at the start or end of
        # the long_id bytearray
        while long_id[0] == bytearray([0]):
            long_id = long_id[1:]
        while long_id[-1] == bytearray([0]):
            long_id = long_id[0: len(long_id) - 1]

        # if the block is already in the records
        if self.is_block_known(long_id):
            return True
        else:  # if the blcok is not yet in the records
            # result[2] is the name of the index file in which the ID should be
            # recorded
            right_index_file = self.which_file(short_from_long_id(long_id))
            self.index_lock.acquire()
            f = open(os.path.join(self.index_dir, right_index_file), "ab")
            f.write(
                to_b255_no_0s(len(long_id))
                + bytearray([0])
                + long_id
                + bytearray([0, 0, 0, 0, 0, 0])
            )
            f.close()
            log.info(f"{self.name}:  Block is new. Added block to ID Records.")
            if self.number_of_known_ids is not None:
                self.number_of_known_ids += 1

            self.current_file_length += 1
            if self.current_file_length >= self.max_num_blocks_per_file:
                self.create_new_index_file()

            self.index_lock.release()
            self.cache_block(long_id)

            # it is important to save the block datafile only after saving its
            # ID in an index file, in case this function gets interrupted,
            # because when checking if a block is known, the block datafiles
            # are checked, not the index-files
            self.save_block(block)
            return False

    def index_file_reader(
        self, task: str, args: str | bytearray
    ) -> int | bytearray | list[bytearray] | None:
        """Read index files.

        This function can be used to perform a range of different tasks
        that require an index file to be read,
        such as looking up Block IDs or counting the number of IDs.

        Tasks:
            - find_block: checks if a Block ID exists in the block records
                task: must be "find_block"
                args: string block_id: the ID to lookup, in its long form
                Returns:
                    bool found: whether or not the ID was found in the found
            - count_ids: counts how many IDs are in the specified index file
                task: must be "count_ids"
                args: string filename: the name of the index file in which to
                    count the ID entries
                Returns: int count: the number of IDs stored in the specified
                    index file
            - list_ids: returns a list of all the IDs in the specified index
                    file
                task: must be "list_ids"
                args: string filename: the name of the index file to extract
                    all IDs from
                Returns: bytearray ID

        Aegs:
            See the 'Tasks' section above for explanations on specific
                    meanings and usage.
            - task (str): sets what task this function will perform,
                    determined by why we need to read an index file
            - args: the parameters specific to the task to perform
        Returns:
            If the index file read was found to be corrupt, None is returned.
            Otherwise, the return variables depend on what task was performed.
            See the 'Tasks' section.

        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        find_id = False
        count_ids = False
        list_ids = False
        if task == "find_block":
            find_id = True
            block_id = args
            file = self.which_file(block_id)
        elif task == "count_ids":
            count_ids = True
            file = args
        elif task == "list_ids":
            list_ids = True
            file = args
            entry_list = []
        else:
            log.error(
                f"{self.name}: error: index_file_reader was called with an "
                "invalid task: " + task
            )
            return None
        if not file:
            return None
        self.index_lock.acquire()

        if not os.path.exists(os.path.join(self.index_dir, file)):
            log.error(
                f"BlockRecords {task}: Index file doesn't exist: {file}\n"
                f"{traceback.format_stack(limit=8)}"
            )
            self.index_lock.release()
            return None

        ID_count = 0  # counter for counting the number of IDs in the file
        # gets called when end of file is reached or error is found in file

        def Finished(success: bool) -> int | bytearray | list[bytes] | None:
            file_reader.close()
            self.index_lock.release()
            if not success:
                log.error(
                    f"{self.name}: BlockRecords: error reading an index file."
                )
                return None

            if find_id:
                # The end of the file was reached without finding the ID.
                return None
            elif count_ids:
                return ID_count
            elif list_ids:
                return entry_list
            log.error(
                f"{self.name}: BlockRecords: Bug in index_file_reader(), this "
                "line isn't to be reached."
            )
            return None

        # checking  if the ID is recorded in the file
        file_reader = open(os.path.join(self.index_dir, file), "rb")
        # Loop reading one ID after the other:
        while True:
            # Reading the length of the next ID
            next_id_length_255 = bytearray([])

            # going through one byte of the block_id length number after the
            # other until we reach 0, the code for the end of the block_id
            # length number
            while True:
                byte = file_reader.read(1)
                # if we've finished reading the ID length code, break the loop
                if byte == bytearray([0]):
                    break
                elif len(byte) == 0:  # if we've reached the end of the file
                    return Finished(True)
                else:  # we're still reading the block_id length number
                    next_id_length_255 = next_id_length_255 + byte
            # decoding the bytearray representation of the length
            next_id_length = from_b255_no_0s(next_id_length_255)

            # reading the next ID
            index_entry = bytearray(file_reader.read(next_id_length))

            # making sure the end code is in place
            if file_reader.read(6) != bytearray([0, 0, 0, 0, 0, 0]):
                log.error(
                    f"{self.name}: error in the Block ID records in index file"
                    f" {file}. Block ID entry was not followed by the entry "
                    "separator bytearray([0,0,0,0,0,0])."
                )
                file_reader.close()
                # ID_count (we don't know how many IDs were stored in the file)
                self.index_lock.release()

                return None
            # finished reading index entry

            if find_id:
                # comparison compatible with short id and long id
                # if it's the block we're looking for
                if (
                    index_entry == block_id
                    or short_from_long_id(index_entry) == block_id
                ):
                    file_reader.close()
                    # True: that the block was found
                    self.index_lock.release()
                    return index_entry
            elif list_ids:
                entry_list.append(index_entry)
            # incrementing the counter that keeps track of how many IDs have
            # been processed so far
            ID_count = ID_count + 1
        self.index_lock.release()

    def is_block_known(self, block_id: bytearray) -> bool:
        """Check if the given block ID exists in our block records.

        This method is faster than find_block.

        Args:
            block_id (str): the ID to lookup, in its long or short form
        Returns:
            bool found: whether or not the ID was found in the found
        """
        block_datafilepath = self.get_block_datafile_path(block_id)

        return os.path.exists(block_datafilepath)

    def get_cached_block(self, short_id: bytearray) -> bytearray | None:
        """Given a block's short ID, look up its long ID in our cache."""
        short_id = short_from_long_id(short_id)  # ensure it's a short ID
        cache_entry = [
            record for record in self.block_id_cache if record[0] == short_id
        ]
        if cache_entry:
            return cache_entry[0][1]
        return None

    def cache_block(self, long_id: bytearray) -> None:
        """Cache a block's long ID."""
        short_id = short_from_long_id(long_id)
        if short_id == long_id:
            log.warning("BlockRecords.cache_block: short_id was passed")
            return

        # check if it's already cached
        cache_entry = [
            record for record in self.block_id_cache if record[0] == short_id
        ]
        if cache_entry:
            return

        self.block_id_cache.append((short_id, long_id))
        if len(self.block_id_cache) > MAX_BLOCKS_CACHE:
            self.block_id_cache.pop(0)

    def find_block(self, short_id: bytearray) -> bytearray | None:
        """Given a block's short ID, return its long ID.

        Checks our cache first, then checks the index files.
        """
        short_id = short_from_long_id(short_id)  # ensure it's a short ID
        if not short_id:
            raise InvalidBlockIdError()
        # check cache
        cache_entry = self.get_cached_block(short_id)
        if cache_entry:
            return cache_entry

        # lookup block from index
        long_id: bytearray = self.index_file_reader("find_block", short_id)
        if not long_id:
            return None

        # cache result
        self.cache_block(long_id)
        return long_id  # return long ID

    def count_ids(self, filename: str) -> int | None:
        """Count how many IDs are in the specified index file.

        Args:
            filename (str): the name of the index file in which to count the ID
                            entries
        Returns:
            - If the file is corrupt, returns None. Otherwise,
            - int count: the number of IDs stored in the specified index file
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        result: int = self.index_file_reader("count_ids", filename)
        if result is None:
            return 0
        else:
            return result

    def list_ids(self, filename: str) -> list[bytearray]:
        """Get a list of all the IDs recorded in the specified index-file.

        Args:
            filename(str): the name of the index file to extract all IDs from
        Returns:
            list(bytearray)
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        self.block_record_initialised.wait()
        result: list[bytearray] = self.index_file_reader("list_ids", filename)
        if result is None:
            log.warning(
                f"{self.name}:  BlockRecords.list_ids: index_file_reader "
                "returned None"
            )
            return []
        else:
            return result

    def which_file(self, short_id: bytearray) -> str | None:
        """Work out in which index-file the specified ID should be stored."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        while short_id[-1] == 0:
            short_id = short_id[:-1]
        timestamp = decode_short_id(short_id)["creation_time"]
        right_file = None

        for file, file_time in self.index_files_times[::-1]:
            if file_time < timestamp:
                right_file = file
                break
        if right_file is None:
            message = (
                f"{self.name} Block Records: Asked for block that is "
                "older than our records."
            )
            message += str(timestamp) + self.name
            log.warning(message)
        return right_file

    def save_block(self, block: Block) -> None:
        """Save all the given block's data & metadata in the block records."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        self.block_record_initialised.wait()
        block_datafilepath = self.get_block_datafile_path(block.short_id)
        block_datafile_dir = os.path.dirname(block_datafilepath)
        if not os.path.exists(block_datafile_dir):
            try:
                os.makedirs(block_datafile_dir)
            except FileExistsError:
                pass

        block.save_block_to_file(block_datafilepath)

    def get_block_datafile_path(self, short_id: bytearray) -> str:
        """Get the filepath of a block's block-file."""
        short_id = short_from_long_id(short_id)
        ipfs_cid = decode_short_id(short_id)["ipfs_cid"]
        return os.path.join(self.received_blocks_dir, ipfs_cid[:4], ipfs_cid)

    def load_block(self, short_id: bytearray) -> Block | None:
        """Load a block Block object from the block records."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        if not self.is_block_known(short_id):
            return None
        self.block_record_initialised.wait()
        ipfs_cid = decode_short_id(short_id)["ipfs_cid"]
        block_data = ipfs.files.read(ipfs_cid)
        block = self.read_block(block_data, ipfs_cid, live=False)
        return block

    def create_index(self) -> None:
        """Create a list of all index files constituting the Block ID Records.

        If no index files are found, create the first index file.
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        log.info(f"{self.name}:  Loading the record of known blocks...")
        # loading a list of all index files for the ID records
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)
        index_files = os.listdir(self.index_dir)
        index_files.sort()
        # if there are no index files at all, create one
        if len(index_files) == 0:
            index_files = [self.create_new_index_file()]
        # going through all the IDs in the file
        ID_count = self.count_ids(index_files[0])
        self.current_file_length = ID_count
        if len(index_files) == 1:  # if there is only 1 index file
            if ID_count > -1:
                self.number_of_known_ids = ID_count

        self.index_files_times = []
        for file in index_files:
            self.index_files_times.append((file, string_to_time(file)))

    def create_new_index_file(self) -> str:
        """Create a new index file for storing block IDs."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        filename = time_to_string(datetime(2022, 1, 1))
        f = open(os.path.join(self.index_dir, filename), "w+")
        f.close()
        # registering new index file in our list of index files and their
        # creation times
        self.index_files_times.append((filename, string_to_time(filename)))
        # updating the counter for the number of blocks recrded in the latest
        # index file
        self.current_file_length = 0
        return filename

    def load_latest_block_ids(
        self,
        amount: int | None = None,
        since_date: datetime | None = None,
        topics: list | None = None,
    ) -> list[bytearray]:
        """Get the IDs of latest few blocks from the block records.

        The order of the returned blocks is roughly from most recent to oldest,
        but cannot be guaranteed. In the same way it cannot be guaranteed that
        the blocks returned are truely the newest received if the amount
        parameter is set.

        Args:
            amount (int): how many blocks should be returned (None -> no limit)
            since_date (datetime): the maximum age of the blocks to look for
                                (None for no limit)
            topics (str):  string or list of strings of topics to filter by,
                    returning only blocks published on those topics
                    (None for no filtering by topics)

        Returns:
            list[bytearray]: a list of Block IDs
        """
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        self.block_record_initialised.wait()
        # if not amount and not since_date:
        #     return
        if isinstance(topics, str):
            topics = [topics]

        blocks = []
        done = False
        # look through each index file, in order of newest to oldest files
        for file, time in self.index_files_times[::-1]:
            if done:
                break
            # for each block in this index file
            for block_id in self.list_ids(file)[::-1]:
                if done:
                    break
                block_data = decode_long_id(block_id)
                if topics and not [
                    topic for topic in topics if topic in block_data["topics"]
                ]:
                    continue
                if since_date and block_data["creation_time"] < since_date:
                    continue
                blocks.append((block_id, block_data["creation_time"]))
                if amount and len(blocks) >= amount:
                    done = True
                    break
            # if this file was created before the since_date, there is no point
            # in searching through even older index files
            if since_date and time < since_date:
                done = True
                break
        # sort blocks by creation date
        blocks = sorted(blocks, key=lambda params: params[1])

        # return only the block_ids
        return [block_id for block_id, creation_time in blocks]

    def get_genesis_block(self) -> bytearray:
        """Get this blockchain's genesis block."""
        # if we've cached it, return that
        if self._genesis_block_id:
            return self._genesis_block_id

        # get first index file
        file, time = self.index_files_times[0]
        blocks = self.list_ids(file)
        genesis_block_id = blocks[0]
        block_data = decode_long_id(genesis_block_id)
        if not (
            len(block_data["parents"]) == 0
            and "genesis" in block_data["topics"]
        ):
            error_message = "BlockRecords.get_genesis_block not working"
            log.error(error_message)
            raise NotSupposedToHappenError(error_message)

        self._genesis_block_id = genesis_block_id  # cache
        return genesis_block_id

    def ensure_ipfs_pinned(self) -> None:
        """Ensure all block's data-files are pinned on our IPFS node."""
        self.check_alive()  # ensure this Blockchain object isn't shutting down

        ipfs_pins = ipfs.files.list_pins(cids_only=True, cache_age_s=300)
        for subfolder in os.listdir(self.received_blocks_dir):
            subfolder_dir = os.path.join(self.received_blocks_dir, subfolder)
            if not os.path.isdir(subfolder_dir):
                raise NotSupposedToHappenError(
                    f"Walytis: Error in the block records directory "
                    f"{self.received_blocks_dir}\nIt should include only "
                    f"folders, but a file was found: {subfolder}"
                )
            for block_cid in os.listdir(subfolder_dir):
                if block_cid not in ipfs_pins:
                    cid = ipfs.files.publish(
                        os.path.join(subfolder_dir, block_cid)
                    )
                    if not cid == block_cid:
                        log.error(
                            f"Walytis_Beta: ensure_ipfs_pinned: published "
                            f"block's cid is not the same as its file name "
                            f"{self.name} {block_cid}"
                        )
                    else:
                        ipfs.files.pin(block_cid)

    @abstractmethod  # defined in Blockchain
    def check_alive(self) -> None:
        """Raise an exception if this blockchain is not running."""
        pass

    @abstractmethod
    def read_block(
        self, block_data: bytearray, ipfs_cid: str, live: bool = True
    ) -> Block | None:
        """Read a block file, returning a Block object if it is valid."""
        pass
