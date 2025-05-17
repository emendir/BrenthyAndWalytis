"""The exceptions used in Walytis_Beta API.

Users of `walytis_beta_api` should use these classes to catch specific errors,
but should not instantiate and raise them themselves, and the full backwards-
compatibility of their constructors will not be guaranteed.
"""


class WalytisReplyDecodeError(Exception):
    """`walytis_beta_api` couldn't decode a reply from Walytis_Beta."""

    def_message = (
        "error parsing the reply from Walytis_Beta. This is probably a bug."
    )

    def __init__(self, message: str = def_message, reply: str = ""):
        self.message = message
        self.reply = str(reply)

    def __str__(self):
        return self.message + " \n" + self.reply


class WalytisBugError(Exception):
    """Walytis_Beta ran into an exception while processing a request."""

    def_message = (
        "Walytis_Beta ran into a problem processing a request. This is a bug."
    )

    def __init__(self, message: str = def_message, error_message: str = ""):
        self.message = message
        self.error_message = message

    def __str__(self):
        if self.error_message:
            return f"{self.message}\nWalytis says: {self.error_message}"
        return self.message


class NoSuchBlockchainError(Exception):
    """The blockchain mentioned by a request does not exist."""

    message = "We have no blockchain with the specified name/id."

    def __init__(self, blockchain_id: str = "", blockchain_name: str = ""):
        self.blockchain_id = blockchain_id
        self.blockchain_name = blockchain_name

    def __str__(self):
        if self.blockchain_id:
            self.message = "We have no blockchain with the specified id: "
            self.message += self.blockchain_id
        if self.blockchain_name:
            self.message = "We have no blockchain with the specified name: "
            self.message += self.blockchain_name
        return self.message


class BlockchainAlreadyExistsError(Exception):
    """We already participate the blockchain trying to be joined."""

    message = "We already have a blockchain with the specified id or name."

    def __init__(self, blockchain_id: str = "", blockchain_name: str = ""):
        self.blockchain_id = blockchain_id
        self.blockchain_name = blockchain_name

    def __str__(self):
        if self.blockchain_id:
            self.message = (
                "We already have a blockchain with the specified id: "
            )
            self.message += self.blockchain_id
        if self.blockchain_name:
            self.message = (
                "We already have a blockchain with the specified name: "
            )
            self.message += self.blockchain_name
        return self.message


class NoSuchInvitationError(Exception):
    """The invitation mentioned by the request does not exist."""

    message = "This blockchain does not have such a join-key."

    def __init__(self, message: str = message):
        self.message = message

    def __str__(self):
        return self.message


class JoinFailureError(Exception):
    """Joining a blockchain failed."""

    def_message = (
        "Failed to join the specified blockchain. Trying again later may work."
    )

    def __init__(self, message: str = def_message, error_message: str = ""):
        self.message = message
        self.error_message = error_message

    def __str__(self):
        if self.error_message:
            return self.message + "\n" + self.error_message
        return self.message


class BlockNotFoundError(Exception):
    """The block mentioned by the request doesn't exists/isn't known yet."""

    def_message = (
        "Block not found!"
    )

    def __init__(self, message: str = def_message):
        self.message = message

    def __str__(self):
        return self.message


class BlockCreationError(Exception):
    """The walytis_beta blockchain failed to add a block to the blockchain."""

    def_message = "Failed to add a block to a blockchain."

    def __init__(self, message: str = def_message, blockchain_name: str = ""):
        self.message = message
        self.blockchain_name = blockchain_name

    def __str__(self):
        if self.blockchain_name:
            return f"{self.message} Blockchain: {self.blockchain_name}"
        return self.message


class InvalidBlockIdError(Exception):
    """When a variable isn't a valid block ID."""

    def_message = "The given data is not a valid block ID."

    def __init__(
        self, message: str = ""
    ):
        if message:
            self.message = message
        else:
            self.message = self.def_message

    def __str__(self):
        return self.message


class BlockIntegrityError(Exception):
    """A block object doesn't satisfy all the Walytis_Beta block constraints.

    This is due to a software bug or a failed forgery attempt.
    """

    def __init__(
        self, message: str, sought_id: str = "", received_id: str = ""
    ):
        self.message = message
        self.sought_id = sought_id
        self.received_id = received_id

    def __str__(self):
        stri = self.message
        if self.sought_id:
            stri += "\n" + str(self.sought_id)
        if self.received_id:
            stri += "\n" + str(self.received_id)
        return stri


class NotSupposedToHappenError(Exception):
    """When a should-be-impossible situation arises, indicating a bug."""

    def_message = "Something weird happened. This is a bug."

    def __init__(self, message: str = def_message):
        self.message = message

    def __str__(self):
        return self.message


NO_SUCH_BLOCKCHAIN_MESSAGE = "no such blockchain"
NO_SUCH_INVITATION_MESSAGE = "no such join-key"
BLOCK_NOT_FOUND = "block not found"
WALYTIS_BETA_ERROR_MESSAGE = "internal Walytis_Beta error"
BLOCKCHAIN_EXISTS_MESSAGE = "blockchain already exists"