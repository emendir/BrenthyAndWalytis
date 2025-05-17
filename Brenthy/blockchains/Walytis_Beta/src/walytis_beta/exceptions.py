"""Exceptions used in Walytis_Beta."""


class BlockchainTerminatedError(Exception):
    """When a method is called on a blockchain that is shutting down."""


class BlockchainNotInitialised(Exception):
    """When a method is called on a blockchain isn't yet initialised."""
