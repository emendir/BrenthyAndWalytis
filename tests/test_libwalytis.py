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

import _testing_utils
from _testing_utils import mark
if True:
    import os
    os.environ["WALYTIS_BETA_API_TYPE"] = "WALYTIS_BETA_DIRECT_API"
    from Walytis_Beta import  walytis_beta_api
    import Walytis_Beta


def run_walytis():
    Walytis_Beta.run_blockchains()
    mark(True, "Walytis is running")

def on_block_received(block:walytis_beta_api.Block):
    print("test_lib_walyits: Received block!", block.topics)
def test_list_blockchains() -> None:
    """Test that we can create a Walytis blockchain."""
    result = walytis_beta_api.list_blockchains()
    success = isinstance(result, list)

    mark(success, "list blockchains")
def test_create_blockchain() -> None:
    """Test that we can create a Walytis blockchain."""
    global blockchain
    try:
        blockchain = walytis_beta_api.Blockchain.create(
            "TestingBrenthy",
            app_name="BrenthyTester",
            block_received_handler=on_block_received,
        )
    except walytis_beta_api.BlockchainAlreadyExistsError:
        blockchain = walytis_beta_api.Blockchain(
            "TestingBrenthy",
            app_name="BrenthyTester",
            block_received_handler=on_block_received,
        )
    success = isinstance(blockchain, walytis_beta_api.Blockchain)

    mark(success, "create_blockchain")


def stop_walytis():
    Walytis_Beta.terminate()


def run_tests() -> None:
    """Run all tests."""
    run_walytis()
    test_list_blockchains()
    test_create_blockchain()
    stop_walytis()


if __name__ == "__main__":
    run_tests()
