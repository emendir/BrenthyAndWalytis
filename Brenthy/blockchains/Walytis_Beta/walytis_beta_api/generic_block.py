"""Interfaces for `Block` and `Blockchain` classes for blockchain overlays."""

from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class GenericBlock(ABC):
    @abstractclassmethod
    def from_id(
        cls, long_id: bytearray
    ):
        pass

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
        self._ipfs_cid = ""
        self._short_id = bytearray()
        self._long_id = bytearray()
        self._creator_id = bytearray()
        self._creation_time = datetime.utcnow()
        self._topics = []
        self._content = bytearray()
        self._parents = []
        self._file_data = bytearray()

    @property
    def ipfs_cid(self) -> str:
        return self._ipfs_cid

    @property
    def short_id(self) -> bytearray:
        return self._short_id

    @property
    def long_id(self) -> bytearray:
        return self._long_id

    @property
    def creator_id(self) -> bytearray:
        return self._creator_id

    @property
    def creation_time(self) -> datetime:
        return self._creation_time

    @property
    def topics(self) -> list[str]:
        return self._topics

    @property
    def content(self) -> bytearray:
        return self._content

    @property
    def parents(self) -> list[bytearray]:
        return self._parents

    @property
    def file_data(self) -> bytearray:
        return self._file_data
