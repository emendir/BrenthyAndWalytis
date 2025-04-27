"""Interfaces for `Block` and `Blockchain` classes for blockchain overlays."""

from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, Iterable

from walytis_beta_tools._experimental.generic_block import GenericBlock


class GenericBlockchain(ABC):
    @abstractproperty
    def blockchain_id(self) -> str:
        pass

    @abstractproperty
    def block_received_handler(self) -> Callable[[GenericBlock], None] | None:
        pass

    @abstractmethod
    def add_block(
        self, content: bytes, topics: list[str] | str | None = None
    ) -> GenericBlock:
        pass

    @abstractmethod
    def get_blocks(self, reverse: bool = False) -> Iterable[GenericBlock]:
        pass

    @abstractmethod
    def get_block_ids(self) -> Iterable[bytes]:
        pass

    @abstractmethod
    def get_num_blocks(self) -> int:
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

        self._block_received_handler = None

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
