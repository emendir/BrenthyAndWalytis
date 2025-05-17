"""Machinery for processing blocks' ancestries."""

from brenthy_tools_beta import log

from .walytis_beta import Blockchain
from walytis_beta_tools.block_model import decode_long_id, Block


class BlockModel:
    """Representation of a block for purposes of ancestry processing."""

    id: bytearray  # long ID
    parents: list[bytearray]  # list of short IDs
    ancestors: list[bytearray]  # list of long IDs
    oldest_known_generation: list  # list of BlockModels

    def __init__(
        self,
        id: bytearray,
        parents: list[bytearray] | None = None,
        ancestors: list[bytearray] | None = None,
        oldest_known_generation: list | None = None,
    ):
        """Create a BlockModel object."""
        self.blockchain_id = id
        self.parents = parents if parents else []
        self.ancestors = ancestors if ancestors else []
        self.oldest_known_generation = (
            oldest_known_generation if oldest_known_generation else []
        )
        self.parents = (
            parents
            if parents
            else decode_long_id(self.blockchain_id)["parents"]
        )
        self.common_to_all = False


def list_unshared_ancestors(
    blockchain: Blockchain, blocks: list
) -> list[bytearray]:
    """Get all the ancestors the given blocks don't all have in common.

    Args:
        blockchain (Blockchain): the blockchain these blocks belong to
        blocks (list): list of Block objects or block IDs

    Returns:
        list: long IDs of blocks
    """
    # list of the blocks provided, but represented with the BlockModel class
    org_blocks = []
    for block in blocks:
        if isinstance(block, Block):  # if it is a Block object
            long_id = block.long_id
            parents = block.parents
        else:  # if it is a block ID
            long_id = blockchain.find_block(block)  # ensure it's a long ID
            if not long_id:
                error_message = (
                    f"block_ancestry: blockchain {blockchain.name}: couldn't "
                    f"find block {block}"
                )
                log.error(error_message)
                raise Exception(error_message)
            parents = decode_long_id(long_id)["parents"]

        # create a BlockModel to represent this block
        block_model = BlockModel(
            id=long_id,
            parents=parents,
        )

        # add new attribute to keep track of whether this block
        # is known to be an ancestor of all others in org_blocks
        block_model.common_to_all = False
        block_model.oldest_known_generation = [block_model]
        # block_model.ancestors = list([])
        org_blocks.append(block_model)
    all_ancestors_common = False

    while not all_ancestors_common:
        # for each block in org_blocks, resolve one more generation
        for block in org_blocks:
            odg = []  # the new oldest known generation for this block
            for ancestor in block.oldest_known_generation:
                # append ancestors parents (as long IDs) to odg
                for parent in ancestor.parents:
                    long_id = blockchain.find_block(parent)

                    if long_id not in block.ancestors:
                        block.ancestors.append(long_id)

                        block_model = BlockModel(long_id)
                        block_model.common_to_all = ancestor.common_to_all
                        odg.append(block_model)

            block.oldest_known_generation = odg

        # for each block in org_blocks
        # check each ancestor in oldest_known_generation that is not yet
        # marked as common to all and see if it now is

        all_ancestors_common = True  # setting to True for efficient checking
        for block in org_blocks:
            for ancestor in block.oldest_known_generation:
                # ignore ancestors that are already common to all org_blocks
                if ancestor.common_to_all:
                    continue
                common_to_all = True
                for _block in org_blocks:
                    if ancestor.blockchain_id not in _block.ancestors:
                        common_to_all = False
                        all_ancestors_common = False
                        break

                ancestor.common_to_all = common_to_all

    # list of blocks that aren't ancestors to all in org_blocks
    unshared_ancestors = []

    # list of all ancestors we've counted
    all_ancestors = remove_duplicates(
        sum([block.ancestors for block in org_blocks], [])
    )

    for ancestor in all_ancestors:
        common_to_all = True
        for _block in org_blocks:
            if ancestor not in _block.ancestors:
                unshared_ancestors.append(ancestor)
                break
    return remove_duplicates(unshared_ancestors)


def remove_duplicates(array: list) -> list:
    """Remove duplicates from the given list."""
    result = []
    for element in array:
        if element not in result:
            result.append(element)
    return result


def remove_ancestors(
    blockchain: Blockchain, blocks: list[bytearray]
) -> list[bytearray]:
    """Given a list of blocks, remove any which is an ancestors of another.

    Args:
        blockchain (Blockchain): the blockchain these blocks belong to
        blocks (list): list of Block objects or block IDs
    Returns:
        list: long IDs of blocks
    """
    # get a list of all the ancestors any of these blocks have
    # that aren't ancestors of all of these blocks
    unshared_ancestors = list_unshared_ancestors(blockchain, blocks)

    result = []
    for block in blocks:
        # get block long ID
        if isinstance(block, Block):  # if it is a Block object
            long_id = block.long_id
        else:  # if it is a block ID
            long_id = blockchain.find_block(block)  # ensure it's a long ID

        if long_id not in unshared_ancestors:
            result.append(long_id)
    return result
