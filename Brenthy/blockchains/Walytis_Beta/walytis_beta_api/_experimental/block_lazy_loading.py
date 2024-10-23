

from __future__ import annotations
from collections.abc import Generator

from datetime import datetime
from typing import Generic, Type, TypeVar

import ipfs_api

from ..block_model import Block, decode_long_id, short_from_long_id
from ..walytis_beta_interface import (
    BlockIntegrityError,
    BlockNotFoundError,
)


class BlockLazilyLoaded(Block):

    def __init__(self, long_id: bytearray | bytes):
        """Initialise an empty block object, not yet valid on a blockchain."""
        Block.__init__(self)
        if isinstance(long_id, bytes):
            long_id = bytearray(long_id)
        self._long_id: bytearray = long_id

        self._decoded_id = False

    @classmethod
    def from_id(
        cls, long_id: bytearray
    ):
        return cls(long_id=long_id)

    def _decode_id(self) -> None:
        metadata = decode_long_id(self.long_id)
        self._blockchain_version = metadata["blockchain_version"]
        self._ipfs_cid = metadata["ipfs_cid"]
        self._creator_id = metadata["creator_id"]
        self._creation_time = metadata["creation_time"]
        self._topics = metadata["topics"]
        self._content_length = metadata["content_length"]
        self._content_hash_algorithm = metadata["content_hash_algorithm"]
        self._content_hash = metadata["content_hash"]
        self._n_parents = metadata["n_parents"]
        self._parents_hash_algorithm = metadata["parents_hash_algorithm"]
        self._parents_hash = metadata["parents_hash"]
        self._parents = metadata["parents"]

    def _load_all(self) -> None:
        """Load all this Block's fields that are normally loaded lazily."""
        self.short_id
        self.content
        self.file_data

    def _load_content(self) -> None:
        block_data = ipfs_api.read(self.ipfs_cid)
        content_separator = block_data.index(bytearray([0, 0, 0, 0, 0]))
        content = block_data[content_separator + 5:]

        self._content = content
        if not self.check_integrity(ignore_filedata=True):
            raise BlockIntegrityError(
                "Integrity check for BlockLazilyLoaded failed."
            )

    @property
    def short_id(self) -> bytearray:
        if not self._short_id:
            self._short_id = short_from_long_id(self.long_id)
        return self._short_id

    @property
    def content(self) -> bytearray:
        if not self._content:
            self._load_content()
        return self._content

    @property
    def file_data(self) -> bytearray:
        if not self._file_data:
            self.generate_file_data(check_integrity=True)
        return self._file_data

    @property
    def ipfs_cid(self) -> str:
        if not self._decoded_id:
            self._decode_id()
        return self._ipfs_cid

    @property
    def creator_id(self) -> bytearray:
        if not self._decoded_id:
            self._decode_id()
        return self._creator_id

    @property
    def creation_time(self) -> datetime:
        if not self._decoded_id:
            self._decode_id()
        return self._creation_time

    @property
    def topics(self) -> list[str]:
        if not self._decoded_id:
            self._decode_id()
        return self._topics

    @property
    def parents(self) -> list[bytearray]:
        if not self._decoded_id:
            self._decode_id()
        return self._parents

    @property
    def blockchain_version(self) -> tuple[int, int, int]:
        if not self._decoded_id:
            self._decode_id()
        return self._blockchain_version


# a type variable restricted to subclasses of Block
BlockType = TypeVar('BlockType', bound=Block)


class BlocksList(dict, Generic[BlockType]):
    block_class: Type[BlockType]

    def __init__(self, block_class: Type[BlockType]):
        # Store the class type to instantiate later
        self.block_class = block_class

    @classmethod
    def from_block_ids(
        cls: Type['BlocksList[BlockType]'],
        block_ids: list[bytes],
        block_class: Type[BlockType]
    ) -> 'BlocksList[BlockType]':

        if block_ids and bytearray([0, 0, 0, 0]) not in bytearray(block_ids[0]):
            print(block_ids[0])
            raise ValueError(
                "It looks like you passed an short ID or invalid ID as a parameter.")
        if block_ids and isinstance(block_ids[0], bytearray):
            block_ids = [bytes(block_id) for block_id in block_ids]

        # Use dict.fromkeys() to create the dictionary efficiently
        blocks_dict = dict.fromkeys(block_ids, None)

        # Cast the dictionary to an instance of BlocksList
        blocks_list = cls.__new__(cls)  # Create an uninitialized instance of the class

        # Manually initialize the dictionary part with the data
        blocks_list.update(blocks_dict)

        # Manually set the block_class
        blocks_list.block_class = block_class

        return blocks_list

    def add_block_id(self, block_id: bytes | bytearray):
        if bytearray([0, 0, 0, 0]) not in bytearray(block_id):
            raise ValueError(
                "It looks like you passed an short ID or invalid ID as a parameter.")
        if isinstance(block_id, bytearray):
            block_id = bytes(block_id)
        self.update({block_id: None})

    def add_block(self, block: BlockType):
        if not isinstance(block, self.block_class):
            raise ValueError(f"block must be of type {self.block_class}, not {type(block)}")
        dict.__setitem__(self, bytes(block.long_id), block)

    def __getitem__(self,  block_id: bytes) -> BlockType:
        try:
            block = dict.__getitem__(self, block_id)
        except KeyError:
            if bytearray([0, 0, 0, 0]) not in block_id:
                raise ValueError(
                    "It looks like you passed an short ID or invalid ID as a parameter.")
            else:
                raise BlockNotFoundError()
        if not block:
            block = self.block_class.from_id(bytearray(block_id))
            dict.__setitem__(self, block_id, block)
        return block

    def get_block(self, block_id: bytes) -> BlockType:
        return self.__getitem__(block_id)

    def get_blocks(
        self, reverse: bool = False
    ) -> Generator[BlockType, None, None]:
        block_ids = self.get_long_ids()

        # reverse order if desired
        if reverse:
            block_ids = reversed(block_ids)

        for block_id in block_ids:
            yield self.__getitem__(block_id)

    def get_long_ids(self):
        return list(self.keys())

    def get_short_ids(self):
        return [short_from_long_id(long_id) for long_id in list(self.keys())]

    def get_num_blocks(self) -> int:
        return len(self)
