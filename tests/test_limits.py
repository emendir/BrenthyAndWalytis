from tqdm import tqdm
import os
import shutil
import sys
import time

import ipfs_api
import pytest
import testing_utils
from brenthy_docker import BrenthyDocker, delete_containers, build_docker_image

from testing_utils import mark, test_threads_cleanup

NUMBER_OF_JOIN_ATTEMPTS = 10
DOCKER_CONTAINER_NAME = "brenthy_tests_limits"
REBUILD_DOCKER = False
# enable/disable breakpoints when checking intermediate test results
testing_utils.BREAKPOINTS = True

# if you do not have any other important brenthy docker containers,
# you can set this to true to automatically remove unpurged docker containers
# after failed tests
DELETE_ALL_BRENTHY_DOCKERS = True
if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    from brenthy_tools_beta.utils import load_module_from_path

    walytis_beta_api = load_module_from_path(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Brenthy",
            "blockchains",
            "Walytis_Beta",
            "walytis_beta_api",
        )
    )
    walytis_beta_appdata = load_module_from_path(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Brenthy",
            "blockchains",
            "Walytis_Beta",
            "walytis_beta_appdata.py",
        )
    )
    import run
    from walytis_beta_api import Block, Blockchain
    import walytis_beta_api
    walytis_beta_api.log.PRINT_DEBUG = True


brenthy_docker: BrenthyDocker
blockchain: Blockchain
created_block: Block
invitation = ""


def prepare() -> None:
    """Get everything needed to run the tests ready."""
    global brenthy_docker
    if DELETE_ALL_BRENTHY_DOCKERS:
        delete_containers(image="local/brenthy_testing",
                          container_name_substr="brenthy")

    if REBUILD_DOCKER:
        build_docker_image(verbose=False)
    false_id_path = os.path.join(
        walytis_beta_appdata.walytis_beta_appdata_dir, "FALSE_BLOCKCHAIN_ID"
    )
    if os.path.exists(false_id_path):
        shutil.rmtree(false_id_path)

    brenthy_docker = BrenthyDocker(
        image="local/brenthy_testing",
        container_name=DOCKER_CONTAINER_NAME,
        auto_run=False
    )


def stop_brenthy() -> None:
    """Stop Brenthy-Core."""
    run.stop_brenthy()


def test_run_brenthy() -> None:
    """Test that we can run Brenthy-Core."""
    run.TRY_INSTALL = False
    run.log.set_print_level("important")
    try:
        run.run_brenthy()
        print(mark(True), "Run Brenthy")
    except Exception as e:
        print(mark(False), "Failed to run Brenthy!")
        print(e)
        sys.exit()


def test_create_blockchain() -> None:
    """Test that we can create a Walytis blockchain."""
    global blockchain
    if "TestingBrenthy" in walytis_beta_api.list_blockchain_names():
        walytis_beta_api.delete_blockchain("TestingBrenthy")
    blockchain = walytis_beta_api.Blockchain.create(
        "TestingBrenthy",
        app_name="BrenthyTester",
    )
    success = isinstance(blockchain, walytis_beta_api.Blockchain)

    print(mark(success), "create_blockchain")

    time.sleep(2)


NUM_BLOCKS = 1000


def test_add_blocks() -> None:
    """Test that we can add a block to the blockchain."""
    for i in tqdm(range(NUM_BLOCKS)):
        blockchain.add_block("Hello there!".encode())

    mark(blockchain.get_num_blocks() == NUM_BLOCKS + 5, "Added blocks")


@pytest.fixture(scope="session", autouse=True)
def cleanup(request: pytest.FixtureRequest | None = None) -> None:
    """Clean up after running tests with PyTest."""
    brenthy_docker.stop()


def run_tests() -> None:
    """Run all tests."""
    prepare()
    print("\nRunning thorough tests for walytis_beta...")
    test_run_brenthy()

    test_create_blockchain()
    test_add_blocks()
    blockchain.terminate()
    stop_brenthy()
    test_threads_cleanup()


if __name__ == "__main__":
    run_tests()
