"""Test that Walytys' block ancestry analysis functions work properly.

Make sure brenthy isn't running before you run these tests.
Don't run pytest yet, compatibility with it hasn't been fully tested.
Simply execute this script instead.
"""

import os
import sys
from datetime import datetime

from _testing_utils import mark

if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    from blockchains.Walytis_Beta.src.walytis_beta import block_ancestry
    from blockchains.Walytis_Beta.src.walytis_beta_api import (
        short_from_long_id,
    )
    from walytis_beta_tools.block_model import Block
    from blockchains.Walytis_Beta.src.walytis_beta_tools.versions import (
        WALYTIS_BETA_CORE_VERSION,
    )


class BlockchainModel:
    """Model of a blockchain used by the test_block_ancestry_funcs test."""

    blocks: list[Block] = []

    def add_block(self, parents: list | None = None) -> Block:
        """Add a model block, given its parents, to this blockchain model."""
        if not parents:
            parents = []
        content = "TESTING".encode()
        block = Block.from_metadata(
            creator_id="TESTING".encode("utf-8"),
            creation_time=datetime.utcnow(),
            topics=["TESTING"],
            content=content,
            content_length=len(content),
            parents=[short_from_long_id(parent) for parent in parents],
            n_parents=len(parents),
            blockchain_version=WALYTIS_BETA_CORE_VERSION,

            ipfs_cid="FALSE_BLOCK",
            content_hash_algorithm="",
            content_hash=bytearray(),
            parents_hash_algorithm="",
            parents_hash=bytearray(),
            file_data=bytearray(),
        )
        block.generate_content_hash()
        block.generate_parents_hash()
        block.generate_id()
        self.blocks.append(block)
        return block

    def find_block(self, block_id: bytearray) -> bytearray:
        """Given a block ID, get that block's long ID or raise an error."""
        short_id = short_from_long_id(block_id)  # ensure it's a short_id
        for block in self.blocks:
            if block.short_id == short_id:
                return block.long_id
        raise Exception(
            f"BlockchainModel.find_block: block not found: \n{block_id}"
        )


blockchain: BlockchainModel
block0: Block
block1: Block
block2: Block
block3: Block
block4: Block
block5: Block
block6: Block
block7: Block
block8: Block


def test_preparations() -> None:
    """Get everything needed to run the tests ready."""
    global blockchain
    global block0, block1, block2, block3
    global block4, block5, block6, block7, block8
    blockchain = BlockchainModel()
    block0 = blockchain.add_block()
    block1 = blockchain.add_block([block0.short_id])
    block2 = blockchain.add_block([block0.short_id, block1.short_id])
    block3 = blockchain.add_block([block1.short_id, block2.short_id])

    block4 = blockchain.add_block([block2.short_id, block3.short_id])
    block5 = blockchain.add_block([block0.short_id, block4.short_id])

    block6 = blockchain.add_block([block1.short_id, block2.short_id])
    block7 = blockchain.add_block([block0.short_id, block6.short_id])

    block8 = blockchain.add_block([block5.short_id, block7.short_id])
def test_cleanup()->None:
    # _testing_utils.terminate()
    pass

def test_unshared_ancestors() -> None:
    """Test that block_ancestry.list_unshared_ancestors works correctly."""
    blocks = [block5, block7, block8]
    expected_result = [6, 4, 3, 5, 7]
    result = block_ancestry.list_unshared_ancestors(blockchain, blocks)

    # get result in terms of block indeces instead of IDs
    block_ids = [block.long_id for block in blockchain.blocks]
    result = [block_ids.index(ancestor) for ancestor in result]

    result.sort()
    expected_result.sort()

    mark(result == expected_result, "list_unshared_ancestors")


def test_remove_ancestors() -> None:
    """Test that block_ancestry.remove_ancestors works correctly."""
    blocks = [block4, block5, block6, block7, block7, block8]
    expected_result = [8]
    result = block_ancestry.remove_ancestors(blockchain, blocks)

    # get result in terms of block indeces instead of IDs
    block_ids = [block.long_id for block in blockchain.blocks]
    result = [block_ids.index(ancestor) for ancestor in result]

    expected_result.sort()

    result.sort()
    mark(result == expected_result, "remove_ancestors")

import _testing_utils
def run_tests() -> None:
    """Run all tests."""
    print("\nRunning tests for Walytis' ancestry machinery...")
    test_preparations()
    test_unshared_ancestors()
    test_remove_ancestors()
    test_cleanup()


if __name__ == "__main__":
    run_tests()
    _testing_utils.terminate()
