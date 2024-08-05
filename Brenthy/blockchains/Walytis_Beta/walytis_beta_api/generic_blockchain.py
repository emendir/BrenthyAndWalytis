"""Interfaces for `Block` and `Blockchain` classes for virtual blockchains."""

from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from typing import Callable


class GenericBlock(ABC):

    @abstractproperty
    def ipfs_cid(self) -> str:
        pass

    @abstractproperty
    def short_id(self) -> bytearray:
        pass

    @abstractproperty
    def long_id(self) -> bytearray:
        pass

    @abstractproperty
    def creator_id(self) -> bytearray:
        pass

    @abstractproperty
    def creation_time(self) -> datetime:
        pass

    @abstractproperty
    def topics(self) -> list[str]:
        pass

    @abstractproperty
    def content(self) -> bytearray:
        pass

    @abstractproperty
    def parents(self) -> list[bytearray]:
        pass

    @abstractproperty
    def file_data(self) -> bytearray:
        pass


class _GenericBlockImpl(GenericBlock):
    """A GenericBlock class with all abstract properties already declared.

    Inherit from this to reduce boilerplate code in your own child class, but
    you become responsible for remembering to assign values to all the fields!
    """

    def __init__(self):
        """Initialise an empty block object, not yet valid on a blockchain."""
        self.ipfs_cid = ""
        self.short_id = bytearray()
        self.long_id = bytearray()
        self.creator_id = bytearray()
        self.creation_time = datetime.utcnow()
        self.topics = []
        self.content = bytearray()
        self.parents = []
        self.file_data = bytearray()

    @property
    def ipfs_cid(self) -> str:
        return self._ipfs_cid

    @ipfs_cid.setter
    def ipfs_cid(self, ipfs_cid: str) -> None:
        self._ipfs_cid = ipfs_cid

    @property
    def short_id(self) -> bytearray:
        return self._short_id

    @short_id.setter
    def short_id(self, short_id: bytearray) -> None:
        self._short_id = short_id

    @property
    def long_id(self) -> bytearray:
        return self._long_id

    @long_id.setter
    def long_id(self, long_id: bytearray) -> None:
        self._long_id = long_id

    @property
    def creator_id(self) -> bytearray:
        return self._creator_id

    @creator_id.setter
    def creator_id(self, creator_id: bytearray) -> None:
        self._creator_id = creator_id

    @property
    def creation_time(self) -> datetime:
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time: datetime) -> None:
        self._creation_time = creation_time

    @property
    def topics(self) -> list[str]:
        return self._topics

    @topics.setter
    def topics(self, topics: list[str]) -> None:
        self._topics = topics

    @property
    def content(self) -> bytearray:
        return self._content

    @content.setter
    def content(self, content: bytearray) -> None:
        self._content = content

    @property
    def parents(self) -> list[bytearray]:
        return self._parents

    @parents.setter
    def parents(self, parents: list[bytearray]) -> None:
        self._parents = parents

    @property
    def file_data(self) -> bytearray:
        return self._file_data

    @file_data.setter
    def file_data(self, file_data: bytearray) -> None:
        self._file_data = file_data


class GenericBlockchain(ABC):
    @abstractproperty
    def blockchain_id(self) -> str:
        pass

    @abstractproperty
    def block_received_handler(self) -> Callable[[GenericBlock], None] | None:
        pass

    @abstractproperty
    def block_ids(self) -> list[bytearray]:
        pass

    @abstractmethod
    def add_block(
        self, content: bytes, topics: list[str] | str | None = None
    ) -> GenericBlock:
        pass

    @abstractmethod
    def get_block(self, id: bytes) -> GenericBlock:
        pass

    @abstractmethod
    def get_peers(self) -> list[str]:
        pass

    @abstractmethod
    def terminate(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass


class _GenericBlockchainImpl(GenericBlockchain):
    """A GenericBlockchain class with all abstract properties already declared.

    Inherit from this to reduce boilerplate code in your own child class, but
    you become responsible for remembering to assign values to all the fields!
    """

    def __init__(self):
        self.blockchain_id = ""
        self.block_received_handler = None
        self.block_ids = []

    @property
    def blockchain_id(self) -> str:
        return self._blockchain_id

    @blockchain_id.setter
    def blockchain_id(self, blockchain_id: str) -> None:
        self._blockchain_id = blockchain_id

    @property
    def block_received_handler(self) -> Callable[[GenericBlock], None] | None:
        return self._block_received_handler

    @block_received_handler.setter
    def block_received_handler(
        self, block_received_handler: Callable[[GenericBlock], None] | None
    ) -> None:
        self._block_received_handler = block_received_handler

    @property
    def block_ids(self) -> list[bytearray]:
        return self._block_ids

    @block_ids.setter
    def block_ids(self, block_ids: list[bytearray]) -> None:
        self._block_ids = block_ids
