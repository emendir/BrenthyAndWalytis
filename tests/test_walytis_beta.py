"""Test that Walytis' core functionality works, using docker containers.

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
DOCKER_CONTAINER_NAME = "brenthy_test"
REBUILD_DOCKER = True
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
        delete_containers(image="local/brenthy_testing", container_name_substr="brenthy")

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


def on_block_received(block: Block) -> None:
    """Eventhandler for newly created blocks on the test's blockchain."""
    global created_block
    created_block = block


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


def test_get_brenthy_version() -> None:
    """Test that we can communicate with Brenthy-Core via BrenthyAPI."""
    try:
        walytis_beta_api.get_brenthy_version()
        print(mark(True), "get_brenthy_version")
    except Exception as e:
        print(mark(False), "get_brenthy_version")
        print(e)
        sys.exit()


def test_run_docker() -> None:
    """Test that we can run the Brenthy docker container."""
    try:
        brenthy_docker.start()
        print(mark(True), "Run BrenthyDocker")
    except Exception as e:
        print(mark(False), "Failed to run BrenthyDocker")
        print(e)
        sys.exit()


def test_find_peer() -> None:
    """Test that we are connected to the Brenthy docker container via IPFS."""
    success = False
    for i in range(5):
        success = ipfs_api.find_peer(brenthy_docker.ipfs_id)
        if success:
            break

    print(mark(success), "ipfs_api.find_peer")


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

    print(mark(success), "create_blockchain")

    time.sleep(2)


def test_add_block() -> None:
    """Test that we can add a block to the blockchain."""
    block = blockchain.add_block("Hello there!".encode())
    success = (
        block.short_id in blockchain._blocks.get_short_ids() and
        block.long_id in blockchain._blocks.get_long_ids() and
        blockchain.get_block(blockchain._blocks.get_short_ids()[-1]).content.decode()
        == blockchain.get_block(blockchain._blocks.get_long_ids()[-1]).content.decode()
        == "Hello there!"
    )
    print(mark(success), "Blockchain.add_block")


def test_create_invitation() -> None:
    """Test that we can create an invitation for the blockchain."""
    global invitation
    invitation = blockchain.create_invitation(one_time=False)
    success = (
        invitation in blockchain.get_invitations(),
        "newly created invitation is not listed in blockchain's invitations",
    )
    print(mark(success), "Blockchain.create_invitation")


def test_joining() -> None:
    """Test that another node can join the blockchain."""
    if not invitation:
        raise CantRunTestError("Invitation is blank")

    join_python_code = (
        "import walytis_beta_api;"
        f"walytis_beta_api.join_blockchain('{invitation}')"
    )
    test_python_code = ";".join([
        "import walytis_beta_api",
        f"print('{blockchain.blockchain_id}' in "
        "walytis_beta_api.list_blockchain_ids())"
    ]
    )

    result = "-"
    for i in range(NUMBER_OF_JOIN_ATTEMPTS):
        brenthy_docker.run_python_code(join_python_code, print_output=False)
        result = brenthy_docker.run_python_code(
            test_python_code, print_output=False
        ).strip("\n")
        if result == "True":
            break
    success = result == "True"
    print(mark(success), "join_blockchain")


def test_join_id_check() -> None:
    """Test that Walytis detects mismatched blockchain IDs when joining."""
    exception = False
    try:
        walytis_beta_api.join_blockchain_from_zip(
            "FALSE_BLOCKCHAIN_ID",
            os.path.join(
                "..", "Brenthy", "InstallScripts", "BrenthyUpdates.zip"
            ),
        )
    except walytis_beta_api.JoinFailureError:
        exception = True
    success = "FALSE_BLOCKCHAIN_ID" not in walytis_beta_api.list_blockchains()
    print(mark(success and exception), "join blockchain ID check")


def test_delete_blockchain() -> None:
    """Test that we can delete a blockchain."""
    blockchain.terminate()
    walytis_beta_api.delete_blockchain("TestingBrenthy")
    success = (
        "TestingBrenthy" not in walytis_beta_api.list_blockchain_names(),
        "failed to delete blockchain",
    )
    print(mark(success), "delete_blockchain")


def test_list_blockchains() -> None:
    """Test that getting a list of blockchains IDs and names works."""
    walytis_beta_api.list_blockchains()

    found = False
    for id, name in walytis_beta_api.list_blockchains():
        if id == blockchain.blockchain_id and name == blockchain.name:
            found = True
            break
    print(mark(found), "walytis_beta_api.list_blockchains")


def test_list_blockchains_names_first() -> None:
    """Test that getting a list of blockchains works with the names first."""
    all_in_order = walytis_beta_api.list_blockchains(names_first=True) == [
        (name, id) for id, name in walytis_beta_api.list_blockchains()
    ]
    print(
        mark(all_in_order),
        "walytis_beta_api.list_blockchains(names_first=True)",
    )


def test_list_blockchain_ids() -> None:
    """Test that getting a list of blockchains IDs."""
    all_in_order = (
        blockchain.blockchain_id in walytis_beta_api.list_blockchain_ids()
        and walytis_beta_api.list_blockchain_ids()
        == [id for id, name in walytis_beta_api.list_blockchains()]
    )
    print(mark(all_in_order), "walytis_beta_api.list_blockchain_ids")


def test_list_blockchain_names() -> None:
    """Test that getting a list of blockchains names."""
    all_in_order = (
        blockchain.name in walytis_beta_api.list_blockchain_names()
        and walytis_beta_api.list_blockchain_names()
        == [name for id, name in walytis_beta_api.list_blockchains()]
    )
    print(mark(all_in_order), "walytis_beta_api.list_blockchain_names")


class CantRunTestError(Exception):
    """When we can't run tests for some reason."""

    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self):
        return self.message


@pytest.fixture(scope="session", autouse=True)
def cleanup(request: pytest.FixtureRequest | None = None) -> None:
    """Clean up after running tests with PyTest."""
    brenthy_docker.stop()


def run_tests() -> None:
    """Run all tests."""
    prepare()
    print("\nRunning thorough tests for walytis_beta...")
    test_run_brenthy()
    test_get_brenthy_version()
    brenthy_docker.start()

    test_find_peer()
    test_create_blockchain()
    test_add_block()
    test_create_invitation()
    test_joining()
    test_join_id_check()
    test_delete_blockchain()
    # breakpoint()
    brenthy_docker.stop()
    blockchain.terminate()
    stop_brenthy()
    test_threads_cleanup()


if __name__ == "__main__":
    run_tests()
