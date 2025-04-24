"""The exceptions used in Walytis_Beta API.

Users of `walytis_beta_api` should use these classes to catch specific errors,
but should not instantiate and raise them themselves, and the full backwards-
compatibility of their constructors will not be guaranteed.
"""

from walytis_beta_tools.exceptions import(
    WalytisReplyDecodeError,
    WalytisBugError,
    NoSuchBlockchainError,
    BlockchainAlreadyExistsError,
    NoSuchInvitationError,
    JoinFailureError,
    BlockNotFoundError,
    BlockCreationError,
    InvalidBlockIdError,
    BlockIntegrityError,
    NotSupposedToHappenError,
)