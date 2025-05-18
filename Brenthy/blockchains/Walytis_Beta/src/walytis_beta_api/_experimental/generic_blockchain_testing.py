"""Testing functions to check GenericBlockchain implementations' integrity."""
import string
import random
from random import randint
from .generic_blockchain import GenericBlockchain, GenericBlock
from walytis_beta_api import Blockchain
from termcolor import colored as coloured
BREAKPOINTS = False
PYTEST = True  # whether or not this script is being run by pytest

# set the range of topic-lengths to test when adding blocks,
# from 0 to this value
N_BLOCK_TOPICS_TO_TEST = 4


def mark(success: bool, message: str, error: Exception | None = None) -> None:
    """Handle test results in a way compatible with and without pytest.

    Prints a check or cross and message depending on the given success.
    If pytest is running this test, an exception is thrown if success is False.

    Args:
        success: whether or not the test succeeded
        message: short description of the test to print
        error: Exception to raise/print in case of failure
    """
    if success:
        mark = coloured("✓", "green")
    else:
        mark = coloured("✗", "red")

    print(mark,message)
    if not success:
        if PYTEST:
            if error:
                raise error
            raise Exception(f'Failed at test: {message}')
        if error:
            print(str(error))
        if BREAKPOINTS:
            breakpoint()


def generate_random_bytes():
    data_length = randint(1, 100)
    data = bytearray([0]) * data_length
    for i in range(data_length):
        data[i] = randint(0, 255)
    return data


def generate_random_string(length=8) -> str:
    # Choose from lowercase and uppercase letters
    # letters = string.ascii_letters  # This is a-zA-Z
    letters = string.printable  # all printable characters
    return ''.join(random.choice(letters) for _ in range(length))


def test_add_block(blockchain: GenericBlockchain, n_topics: int) -> GenericBlock:
    content = generate_random_bytes()

    topics = [generate_random_string(randint(1, 5)) for i in range(n_topics)]
    block_1 = blockchain.add_block(content, topics)

    mark(
        blockchain.get_block_ids()[-1] == block_1.long_id,
        f"NT: {n_topics} - Blockchain.get_block_ids"
    )
    mark(
        blockchain.get_block(-1).short_id == block_1.short_id,
        f"NT: {n_topics} - Blockchain.get_block"
    )
    mark(
        blockchain.get_block(-1).content == block_1.content,
        f"NT: {n_topics} - Block.content"
    )
    mark(
        blockchain.get_block(-1).topics == block_1.topics,
        f"NT: {n_topics} - Block.topics"
    )
    return block_1


def test_generic_blockchain(blockchain_type, **kwargs) -> GenericBlockchain:
    if not issubclass(blockchain_type, GenericBlockchain):
        raise ValueError(
            "The parameter `blockchain_type` must be a class that inherits "
            "`walytis_beta_api._experimental.generic_blockchain.GenericBlockchain`"
        )
    blockchain: GenericBlockchain = blockchain_type(**kwargs)
    mark(
        blockchain.get_num_blocks() == 0,
        "Provided blockchain shouldn't expose blocks yet"
    )
    blocks = [
        test_add_block(blockchain, i) for i in range(N_BLOCK_TOPICS_TO_TEST)
    ]

    # check that the last few block IDs are the created blocks
    success = True
    for i, block in enumerate(blocks):
        expected_index = i - len(blocks)
        if blockchain.get_block_ids()[expected_index] != block.long_id:
            success = False

    mark(success, "No hidden blocks exposed")

    long_block_ids = blockchain.get_block_ids()
    blockchain.terminate()
    blockchain: GenericBlockchain = blockchain_type(**kwargs)
    mark(
        long_block_ids == blockchain.get_block_ids(),
        "block_ids correctly reloaded"
    )

    return blockchain


def test_preparations():
    global blockchain
    blockchain = Blockchain.create()


def test_cleanup():

    blockchain.delete()


def run_tests():
    print("Running tests for GenericBlockchain features...")

    test_preparations()

    test_generic_blockchain(Blockchain, blockchain_id=blockchain.blockchain_id)
    test_cleanup()


if __name__ == "__main__":
    PYTEST = False
    BREAKPOINTS = False
    run_tests()
