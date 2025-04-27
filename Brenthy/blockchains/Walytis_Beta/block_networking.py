"""The networking machinery of the Block class."""

# from random import seed
# from random import randint
import json
import os
from tempfile import NamedTemporaryFile

from brenthy_tools_beta import log
from brenthy_tools_beta.utils import (  # pylint: disable=unused-import
    bytes_to_string,
)

from walytis_beta_tools import block_model

from .networking import ipfs
PREFERRED_HASH_ALGORITHM = "sha512"


class Block(block_model.Block):
    """The Walytis_Beta block.

    The networking functionality is defined in this child class,
    its parent block_model.Block contains the more fundamental functionality.
    """

    def publish_and_generate_id(
        self, blockchain_id: str, skip_pubsub: bool = False
    ) -> None:
        """Publish this block, generating its long ID."""
        # make sure all the necessary components of the short_id have been set
        if len(self.creator_id) != 0 and len(self._content_hash) != 0:
            self._ipfs_cid = self.publish_file_data()
            self.generate_id()
            if not skip_pubsub:
                self.announce_block(blockchain_id)

    def publish_file_data(self) -> str:
        """Put this block's block file on IPFS."""
        log.info("Publishing file...")
        if not (len(self.file_data) > 0):
            error_message = (
                "Walytis_Beta: Block.publish_file_data: file_data is empty"
            )
            log.error(error_message)
            raise ValueError(error_message)
        with NamedTemporaryFile(delete=False) as tempf:
            tempf.write(self.file_data)
            tempf.close()
            cid = ipfs.files.predict_cid(tempf.name)
            if cid in ipfs.files.list_pins(cache_age_s=1000):
                log.error(
                    "Block.publish_file_data: "
                    "IPFS content with this CID already exists!"
                )
                raise IpfsCidExistsError()
            cid = ipfs.files.publish(tempf.name)
            os.remove(tempf.name)
            ipfs.files.pin(cid)
            return cid

    def announce_block(self, blockchain_id: str) -> None:
        """Publish a PubSub message about the new block."""
        data = json.dumps(
            {
                "message": "New block!",
                "block_id": bytes_to_string(self.short_id),
            }
        ).encode()

        ipfs.pubsub.publish(blockchain_id, data)


class IpfsCidExistsError(Exception):
    """When publishing a new block but the intended IPFS CID already exists."""

    message = "An IPFS file with this content ID already exists!"

    def __str__(self):
        """Get this exception's error message."""
        return self.message
