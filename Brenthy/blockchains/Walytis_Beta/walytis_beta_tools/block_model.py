"""The fundamental machinery constituting Blocks."""

import hashlib
from copy import deepcopy

# from random import seed
# from random import randint
from datetime import datetime
from secrets import randbits

from brenthy_tools_beta import log
from brenthy_tools_beta.utils import (  # pylint: disable=unused-import
    bytes_from_b255_no_0s,
    bytes_to_b255_no_0s,
    decode_timestamp,
    encode_timestamp,
    from_b255_no_0s,
    to_b255_no_0s,
)
from brenthy_tools_beta.version_utils import decode_version, encode_version

from .exceptions import BlockIntegrityError, InvalidBlockIdError
from ._experimental.generic_block import _GenericBlockImpl as GenericBlock

PREFERRED_HASH_ALGORITHM = "sha512"


class Block(GenericBlock):
    """The Walytis_Beta block.

    This class contains the basic functionality of the Walytis_Beta block,
    used by both Walytis_Beta and walytis_beta_api.
    The networking parts for publishing blocks is in a child class in
    Walytis_Beta.block_networking.
    """

    def __init__(self):
        """Initialise an empty block object, not yet valid on a blockchain."""
        self._ipfs_cid = ""
        self._short_id = bytearray()
        self._long_id = bytearray()
        self._creator_id = bytearray()
        self._creation_time = datetime.utcnow()
        self._topics = []
        self._content = bytearray()
        self._parents = []
        self._file_data = bytearray()

        self._content_length = 0
        self._content_hash_algorithm = ""
        self._content_hash = bytearray()
        self._n_parents = 0
        self._parents_hash_algorithm = ""
        self._parents_hash = bytearray()
        # the file data which gets published on the blockchain
        self._blockchain_version = []

        self._genesis = False

        self.__integrity_checked = False

    @classmethod
    def from_id(
        cls, long_id: bytearray
    ):
        block = cls()
        block._long_id = long_id
        return block

    @classmethod
    def from_metadata(
        cls,
        ipfs_cid: str,
        creator_id: bytearray,
        creation_time: datetime,
        topics: list[str],
        content_length: int,
        content_hash_algorithm: str,
        content_hash: bytearray,
        content: bytearray,
        n_parents: int,
        parents_hash_algorithm: str,
        parents_hash: bytearray,
        parents: list[bytearray],
        file_data: bytearray,
        blockchain_version: tuple,

    ) -> 'Block':
        """Create a block object with the given fields.

        CAREFUL: No checks or generations are performed.
        """
        block = cls()
        block._ipfs_cid = ipfs_cid
        block._creator_id = creator_id
        block._creation_time = creation_time
        block._topics = topics
        block._content_length = content_length
        block._content_hash_algorithm = content_hash_algorithm
        block._content_hash = content_hash
        block._content = content
        block._n_parents = n_parents
        block._parents_hash_algorithm = parents_hash_algorithm
        block._parents_hash = parents_hash
        block._parents = parents
        block._file_data = file_data
        block._blockchain_version = blockchain_version
        return block

    def generate_content_hash(self) -> bytearray | None:
        """Generate the cryptographic hash of this block's content.

        Returns:
            bytearray: this block's content hash
        """
        self._content_hash_algorithm = PREFERRED_HASH_ALGORITHM
        if not self.content:
            log.error("Block Hash Generation: empty content")
            return None
        hashGen = hashlib.sha512()
        hashGen.update(self.content)
        content_hash = bytearray.fromhex(hashGen.hexdigest())

        # removing 0s:
        self._content_hash = bytes_to_b255_no_0s(content_hash)
        return self._content_hash

    def generate_parents_hash(self) -> bytearray:
        """Generate the hash of this block's parents' parents-hashes.

        Returns:
            bytearray: this block's parents-hash
        """
        self._parents_hash_algorithm = PREFERRED_HASH_ALGORITHM

        if self._n_parents == 0:  # genesis block
            hashGen = hashlib.sha512()
            hashGen.update(
                self.creator_id
                + encode_timestamp(self.creation_time)
                + to_b255_no_0s(randbits(512))
            )
            parents_hash = bytearray.fromhex(hashGen.hexdigest())
        else:
            # collect a list of parent blocks' parents_hashes
            parent_hashes = bytearray([])
            for parent_id in self.parents:
                parent_hash = decode_short_id(parent_id)["parents_hash"]
                # decode parent hash from its 0-less form
                parent_hash = bytes_from_b255_no_0s(parent_hash)  # returns int

                parent_hashes += parent_hash
            # parents_hash is hash of parent_hashes
            hashGen = hashlib.sha512()
            hashGen.update(parent_hashes)
            parents_hash = bytearray.fromhex(hashGen.hexdigest())

        # removing 0s:
        self._parents_hash = bytes_to_b255_no_0s(parents_hash)
        return self._parents_hash

    def check_integrity(self, ignore_filedata: bool = False) -> bool:
        """Make sure this block's data is complete, self-consistent and valid.

        Args:
            ignore_filedata: if True, checking filedata is skipped, though
                                only if the `file_data` attribute is `None`

        Returns:
            bool: whether this block's data is self-consistent and valid.
        """
        if not self._blockchain_version:
            log.warning("Block Integrity Check: blockchain_version not set.")
            return False
        if not self.ipfs_cid:
            log.warning("Block Integrity Check: ipfs_cid not set.")
            return False
        if not self.creator_id:
            log.warning("Block Integrity Check: creator_id not set.")
            return False
        if not self.creation_time:
            log.warning("Block Integrity Check: creation_time not set.")
            return False
        if not self.topics:
            log.warning("Block Integrity Check: topics not set.")
            return False
        if not self._content_length:
            log.warning("Block Integrity Check: Content length not set.")
            return False
        if not self._content_hash_algorithm:
            log.warning(
                "Block Integrity Check: content_hash_algorithm not set."
            )
            return False
        if not self._content_hash:
            log.warning("Block Integrity Check: Hash not set.")
            return False
        # if not self._n_parents:
        #     log.warning("Block Integrity Check: n_parents not set.")
        #     return None
        if not self._parents_hash_algorithm:
            log.warning(
                "Block Integrity Check: parents_hash_algorithm not set."
            )
            return False
        if not self._parents_hash:
            log.warning("Block Integrity Check: parents_hash not set.")
            return False
        if not self.short_id:
            log.warning("Block Integrity Check: short_id not set.")
            return False
        if not self.long_id:
            log.warning("Block Integrity Check: long_id not set.")
            return False

        # only skip checking file data if it is not set
        if ignore_filedata and self.file_data is not None:
            ignore_filedata = False

        if not self.file_data and not ignore_filedata:
            log.warning("Block Integrity Check: filedata not set.")
            return False

        # check if encoded content length matches actual block content length
        if not len(self.content) == self._content_length:
            log.warning("Block INtegrity Check: content length incorrect")
            return False
        # checking if encoded parents count matches actual parent's count
        if not len(self.parents) == self._n_parents:
            log.warning("Block Integrity Check: number of parents incorrect")
            return False

        # check if parents are sorted
        sorted_parents = deepcopy(self.parents)
        sorted_parents.sort()
        if self.parents != sorted_parents:
            log.warning("Block Integrity Check: parents blocks aren't sorted")
            return False

        # Checking generated parts

        # keeping a copy of old generated parts
        old_short_id = deepcopy(self.short_id)
        old_long_id = deepcopy(self.long_id)
        old_content_hash = deepcopy(self._content_hash)
        old_parents_hash = deepcopy(self._parents_hash)
        if not ignore_filedata:
            old_file_data = deepcopy(self.file_data)

        # checking content hash
        self.generate_content_hash()
        # compare the encoded content-hash with the generated content-hash
        if self._content_hash != old_content_hash:
            log.warning("Block Integrity Check: hash does not match.")
            # restoring old non-matching content_hash
            self._content_hash = old_content_hash
            return False

        if self._n_parents > 0:  # genesis blocks' parents can't be checked
            # checking parents hash
            self.generate_parents_hash()
            # comparing the encoded parents-hash with the generated hash
            if self._parents_hash != old_parents_hash:
                log.warning(
                    "Block Integrity Check: parents_hash does not match."
                )
                # restoring old non-matching content_hash
                self._parents_hash = old_parents_hash
                return False

            # ensure all parent blocks have older timestamps than this block
            if [
                parent_id
                for parent_id in self.parents
                if (
                    decode_short_id(parent_id)["creation_time"]
                    > self.creation_time
                )
            ]:
                error_message = (
                    "Block Integrity Check: Parent block's creation time "
                    "is greater than this block's creation time "
                    f"{self.creation_time}. This is most likely due to this "
                    "node's clock not being synchronised."
                )
                log.warning(error_message)
                return False

        # Checking if file_data matches block properties if they are ALL set
        # trying to generate file-data anew from block properties
        self.generate_file_data(check_integrity=False)

        # if the block's file-data and all other properties were set,
        # and the set file-data didn't match all the other propertie,
        # reset the initially set inconsistent file-data property
        if not ignore_filedata and old_file_data != self.file_data:
            self._file_data = old_file_data
            log.warning(
                "Block Integrity Check: File-data doesn't match block fields."
            )
            return False

        # check if short_id matches block properties
        self.generate_id()
        if old_short_id != self.short_id:
            self._short_id = old_short_id
            log.warning(
                "Block Integrity Check: short ID doesn't match block fields."
            )
            return False
        if old_long_id != self.long_id:
            self._long_id = old_long_id
            log.warning(
                "Block Integrity Check: long ID doesn't match block fields."
            )
            return False

        # at this point all integrity tests have been passed
        if not ignore_filedata:
            self.__integrity_checked = True
        return True

    def generate_id(self) -> bytearray | None:
        """Generate this block's ID.

        Returns:
            bytearray: this block's long ID
        """
        # make sure all the necessary components of the short_id have been set
        if not self._blockchain_version:
            log.warning("Block.generate_id(): blockchain_version not set.")
            return None
        if not self.ipfs_cid:
            log.warning("Block.generate_id(): ipfs_cid not set.")
            return None
        if not self.creator_id:
            log.warning("Block.generate_id(): creator_id not set.")
            return None
        if not self.creation_time:
            log.warning("Block.generate_id(): creation_time not set.")
            return None
        if not self.topics:
            log.warning("Block.generate_id(): topics not set.")
            return None
        if not self._content_length:
            log.warning("Block.generate_id(): Content length not set.")
            return None
        if not self._content_hash_algorithm:
            log.warning("Block.generate_id(): content_hash_algorithm not set.")
            return None
        if not self._content_hash:
            log.warning("Block.generate_id(): Hash not set.")
            return None
        # if not self._n_parents:
        #     log.warning("Block.generate_id(): n_parents not set.")
        #     return None
        if not self._parents_hash_algorithm:
            log.warning("Block.generate_id(): parents_hash_algorithm not set.")
            return None
        if not self._parents_hash:
            log.warning("Block.generate_id(): parents_hash not set.")
            return None

        self._short_id = bytearray(
            encode_version(self._blockchain_version)
            + bytearray([0, 0])
            + self.ipfs_cid.encode()
            + bytearray([0, 0])
            + self.creator_id
            + bytearray([0, 0])
            + encode_timestamp(self.creation_time)
            + bytearray([0, 0])
            + bytearray([0]).join([topic.encode() for topic in self.topics])
            + bytearray([0, 0])
            + to_b255_no_0s(self._content_length)
            + bytearray([0, 0])
            + self._content_hash_algorithm.encode()
            + bytearray([0, 0])
            + self._content_hash
            + bytearray([0, 0])
            + to_b255_no_0s(self._n_parents)
            + bytearray([0, 0])
            + self._parents_hash_algorithm.encode()
            + bytearray([0, 0])
            + self._parents_hash
        )

        # Generate long ID:

        # add separator between short ID and parents
        long_id = self._short_id + bytearray([0, 0, 0, 0])

        # add parents, separated by [0,0,0]
        long_id += bytearray([0, 0, 0]).join(self.parents)

        self._long_id = long_id

        decode_long_id(long_id)
        return long_id

    def generate_file_data(
        self, check_integrity: bool = False
    ) -> bytearray | None:
        """Generate this block's block file.

        Encodes all the block's data and metadata into a bytearray.

        Args:
            check_integrity (bool): ensure that the block's data is consitent,
                                    raise an exception if not
        Returns:
            bytearray: the block's block-file data
        """
        try:
            data = bytearray(
                encode_version(self._blockchain_version)
                + bytearray([0, 0])
                + self.creator_id
                + bytearray([0, 0])
                + encode_timestamp(self.creation_time)
                + bytearray([0, 0])
                + bytearray([0]).join(
                    [topic.encode() for topic in self.topics]
                )
                + bytearray([0, 0])
                + to_b255_no_0s(self._content_length)
                + bytearray([0, 0])
                + self._content_hash_algorithm.encode()
                + bytearray([0, 0])
                + self._content_hash
                + bytearray([0, 0])
                + to_b255_no_0s(self._n_parents)
                + bytearray([0, 0])
                + self._parents_hash_algorithm.encode()
                + bytearray([0, 0])
                + self._parents_hash
            )
            if self.parents:
                data += bytearray([0, 0, 0, 0]) + bytearray([0, 0, 0]).join(
                    self.parents
                )
            data += bytearray([0, 0, 0, 0, 0]) + self.content

            self._file_data = data

            if check_integrity and not self.check_integrity():
                self._file_data = None
                raise BlockIntegrityError("Integrity check failed")
            return self.file_data
        except Exception as e:
            log.error("Failed to generate block data.\n" + str(e))
            return None

    def save_block_to_file(self, path: str) -> None:
        """Write this block's block-file-data to a file.

        Args:
            path (str): the filepath to write the blockfile to.
        """
        if len(self.file_data) > 0:
            file = open(path, "wb")
            file.write(self.file_data)
            file.close()
        else:
            log.error("Couldn't save block to file cause data is null.")


def decode_short_id(short_id: bytearray) -> dict:
    # pylint: disable=trailing-whitespace
    """Extract all the information of a block that is encoded in its ID.

    Args:
        short_id (bytearray): the block ID to decode

    Returns:
        dict: a dictionary containing all the block properties extracted from
            the block ID
        `blockchain_version` (list): Walytis_Beta version of the block
        `ipfs_cid` (str): the IPFS content ID the block was published with
        `creator_id` (bytearray): the ID of the block's creator
        `creation_time` (datetime): the time at which the block was created
        `topics` (list<str>): list of topics which this block belongs to
        `content_length` (int): length of block content in bytes
        `content_hash_algorithm` (str): hash algorithm used for content_hash
        `content_hash` (str): the cryptographic hash of the block's content
        `n_parents` (int): the number of parent blocks which this block has
        `parents_hash_algorithm` (str): hash algorithm used for parents_hash
        `parents_hash` (str): the cryptographic hash of the block's parents
    """
    while short_id[-1] == 0:
        short_id = short_id[:-1]
    metadata = short_id.split(bytearray([0, 0]))
    # log.important(str(metadata))
    topics = [
        element.decode("utf-8")
        for element in metadata[4].split(bytearray([0]))
    ]
    try:
        return {
            "blockchain_version": decode_version(metadata[0]),
            "ipfs_cid": metadata[1].decode("utf-8"),
            "creator_id": metadata[2],
            "creation_time": decode_timestamp(metadata[3]),
            "topics": topics,
            "content_length": from_b255_no_0s(metadata[5]),
            "content_hash_algorithm": metadata[6].decode(),
            "content_hash": metadata[7],
            "n_parents": from_b255_no_0s(metadata[8]),
            "parents_hash_algorithm": metadata[9].decode(),
            "parents_hash": metadata[10],
        }
    except:
        raise InvalidBlockIdError()


def decode_long_id(long_id: bytearray) -> dict:
    # pylint: disable=trailing-whitespace
    """Extract all the information of a block that is encoded in its ID.

    Args:
        long_id (bytearray): the block ID to decode
    Returns:
        dict: a dictionary containing all the block properties extracted from
            the block ID
        `blockchain_version` (list): Walytis_Beta version of the block
        `ipfs_cid` (str): the IPFS content ID the block was published with
        `creator_id` (bytearray): the ID of the block's creator
        `creation_time` (datetime): the time at which the block was created
        `topics` (list<str>): list of topics which this block belongs to
        `content_length` (int): length of block content in bytes
        `content_hash_algorithm` (str): hash algorithm used for content_hash
        `content_hash` (str): the cryptographic hash of the block's content
        `n_parents` (int): the number of parent blocks which this block has
        `parents_hash_algorithm` (str): hash algorithm used for parents_hash
        `parents_hash` (str): the cryptographic hash of the block's parents
        `parents` (list): list this block's parent blocks
    """
    if not isinstance(long_id, bytearray):
        raise TypeError(
            f"long_id must be of type bytearray, not {type(long_id)}"
        )
    try:
        short_id, parents_data = long_id.split(bytearray([0, 0, 0, 0]))
        result = decode_short_id(short_id)

        parents = parents_data.split(bytearray([0, 0, 0]))
        if parents == [bytearray([])]:  # genesis block
            parents = []
        result.update({"parents": parents})
    except:
        try:
            _ = decode_short_id(long_id)  # noqa
            error_message = "\nYou passed a short ID instead of a long ID."
        except:
            error_message = ""
        raise InvalidBlockIdError(error_message)
    return result


def short_from_long_id(long_id: bytearray) -> bytearray:
    """Convert a long ID into a short ID.

    Args:
        long_id (bytearray): long block ID
    Returns:
        bytearray: the extracted short block ID
    """
    if not (isinstance(long_id, (bytearray, bytes))):
        raise TypeError(f"long_id must be of type bytearray, not {type(long_id)}")
    try:
        short_id = long_id.split(bytearray([0, 0, 0]))[0]
    except:
        raise InvalidBlockIdError()
    return short_id
