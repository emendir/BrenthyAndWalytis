"""Test that Walytis' core functionality works, quickly.

Make sure brenthy isn't running before you run these tests.
Make sure the brenthy docker image is up to date.
Don't run pytest yet, as test_joining() always fails then for some reason.
Simply execute this script instead.

If testing is interrupted and the docker container isn't closed properly
and the next time you run this script you get an error reading:
    docker: Error response from daemon: Conflict.
    The container name "/brenthy_test" is already in use by container

run the following commands to stop and remove the unterminated container:
    docker stop $(docker ps -aqf "name=^brenthy_test$")
    docker rm $(docker ps -aqf "name=^brenthy_test$")
"""

if True:
    import os
    os.environ["USE_IPFS_NODE"] = "true"
    import _testing_utils
    from _testing_utils import mark
    import walytis_beta_embedded
    import walytis_beta_tools
    import appdirs
    walytis_beta_appdata_dir = os.path.join(appdirs.user_data_dir(), "BrenthyApps")
    walytis_beta_embedded.set_appdata_dir(walytis_beta_appdata_dir)

BC_NAME="LibWalytisTester"
def run_walytis():
    walytis_beta_embedded.run_blockchains()
    mark(True, "Walytis is running")

def on_block_received(block:walytis_beta_embedded.Block):
    print("test_lib_walyits: Received block!", block.topics)
def test_list_blockchains() -> None:
    """Test that we can create a Walytis blockchain."""
    result = walytis_beta_embedded.list_blockchains()
    success = isinstance(result, list)

    mark(success, "list blockchains")
def test_create_blockchain() -> None:
    """Test that we can create a Walytis blockchain."""
    global blockchain
    try:
        blockchain = walytis_beta_embedded.Blockchain.create(
            BC_NAME,
            app_name="BrenthyTester",
            block_received_handler=on_block_received,
        )
    except walytis_beta_tools.exceptions.BlockchainAlreadyExistsError:
        blockchain = walytis_beta_embedded.Blockchain(
            BC_NAME,
            app_name="BrenthyTester",
            block_received_handler=on_block_received,
        )
        print("Blockchain already exists!")
    success = isinstance(blockchain, walytis_beta_embedded.Blockchain)

    mark(success, "create_blockchain")

def test_add_block() -> None:
    """Test that we can add a block to the blockchain."""
    block = blockchain.add_block("Hello there!".encode(), topics="TestTopic")
    success = (
        block.short_id in blockchain._blocks.get_short_ids() and
        block.long_id in blockchain._blocks.get_long_ids() and
        blockchain.get_block(blockchain._blocks.get_short_ids()[-1]).content.decode()
        == blockchain.get_block(blockchain._blocks.get_long_ids()[-1]).content.decode()
        == "Hello there!"
    )
    mark(success, "Blockchain.add_block")
def test_delete_blockchain() -> None:
    """Test that we can delete a blockchain."""
    blockchain.terminate()
    walytis_beta_embedded.delete_blockchain(BC_NAME)
    success = (
        BC_NAME not in walytis_beta_embedded.list_blockchain_names(),
        "failed to delete blockchain",
    )
    mark(success, "delete_blockchain")

def stop_walytis():
    walytis_beta_embedded.terminate()


def run_tests() -> None:
    """Run all tests."""
    run_walytis()
    test_list_blockchains()
    test_create_blockchain()
    test_add_block()
    test_delete_blockchain()
    stop_walytis()


if __name__ == "__main__":
    run_tests()
