"""Test that Walytis blockchains' blocks get synchronised across nodes.

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
import sys
import time
from threading import Thread

import ipfs_api
import testing_utils
from brenthy_docker import BrenthyDocker, delete_containers, build_docker_image
from testing_utils import mark, polite_wait, test_threads_cleanup

REBUILD_DOCKER = True
NUMBER_OF_FIND_ATTEMPTS = 10
NUMBER_OF_JOIN_ATTEMPTS = 10
DOCKER_CONTAINER_NAME = "brenthy_tests_onboarding"
NUMBER_OF_CONTAINERS = 5

# enable/disable breakpoints when checking intermediate test results
testing_utils.BREAKPOINTS = True

# automatically remove all docker containers after failed tests
DELETE_ALL_BRENTHY_DOCKERS = True

if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    walytis_beta_dir = os.path.join(brenthy_dir, "blockchains", "Walytis_Beta")
    print(brenthy_dir)
    print(walytis_beta_dir)
    sys.path.insert(0, brenthy_dir)
    sys.path.insert(0, walytis_beta_dir)
    from brenthy_tools_beta import log
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


brenthy_dockers: list[BrenthyDocker] = []
blockchain: Blockchain


def prepare() -> None:
    """Get everything needed to run the tests ready."""
    if DELETE_ALL_BRENTHY_DOCKERS:
        delete_containers(image="local/brenthy_testing", container_name_substr="brenthy")

    if REBUILD_DOCKER:
        build_docker_image(verbose=False)

    # create the docker containers we will run tests with,
    # but don't run brenthy on them yet
    for i in range(NUMBER_OF_CONTAINERS):

        brenthy_dockers.append(
            BrenthyDocker(
                image="local/brenthy_testing",
                container_name=DOCKER_CONTAINER_NAME + "_" + str(i),
                auto_run=False
            )
        )

    run_brenthy()  # run brenthy on this operating system

    # if "TestingOnboarding" in walytis_beta_api.list_blockchain_names():
    #     walytis_beta_api.delete_blockchain("TestingOnboarding")
    delete_blockchains()  # clean up after failed tests


def run_brenthy() -> None:
    """Run Brenthy."""
    run.TRY_INSTALL = False
    run.run_brenthy()


def stop_brenthy() -> None:
    """Stop Brenthy-Core."""
    run.stop_brenthy()


def delete_blockchains() -> None:
    """Delete all blockchains other than BrenthyUpdates."""
    for bc_id in walytis_beta_api.list_blockchain_ids():
        if not bc_id == "BrenthyUpdates":
            walytis_beta_api.delete_blockchain(bc_id)


def on_block_received(block: Block) -> None:
    """Eventhandler for newly created blocks on the test's blockchain."""
    pass


def get_docker_latest_block_content(
    docker_container: BrenthyDocker,
) -> str:
    """Get the content of the latest block on the specified container."""
    return docker_container.run_python_code(";".join([
        "import walytis_beta_api",
        f"bc = walytis_beta_api.Blockchain('{blockchain.blockchain_id}')",
        "print(bc.get_block(-1).content.decode())",
        "bc.terminate()"
    ]), print_output=False
    ).strip("\n")


def ipfs_connect_to_container(index: int) -> bool:
    """Try to connect to the specified docker container via IPFS."""
    for i in range(NUMBER_OF_FIND_ATTEMPTS):
        if ipfs_api.find_peer(brenthy_dockers[index].ipfs_id):
            return True
    return False


def docker_join_blockchain(index: int) -> bool:
    """Try to make the specified docker container join the test blockchain."""
    invitation = blockchain.create_invitation(one_time=False, shared=True)
    join_python_code = (
        "import walytis_beta_api;"
        f"walytis_beta_api.join_blockchain('{invitation}')"
    )
    test_join_python_code = (
        "import walytis_beta_api;"
        f"print('{blockchain.blockchain_id}' in "
        "walytis_beta_api.list_blockchain_ids())"
    )
    for i in range(NUMBER_OF_JOIN_ATTEMPTS):
        brenthy_dockers[index].run_python_code(
            join_python_code, print_output=False
        )
        result = (
            brenthy_dockers[index]
            .run_python_code(test_join_python_code, print_output=False)
            .strip("\n")
        )

        if result == "True":
            if i > 0:
                print("Number of failed join attempts:", i)
            return True
    return False


def test_sync_block_creation() -> None:
    """Test that blocks are synchronised to other nodes when created."""
    global blockchain
    blockchain = walytis_beta_api.Blockchain.create(
        "TestingOnboarding",
        block_received_handler=on_block_received,
        app_name="test_onboarding.py",
    )

    brenthy_dockers[0].start()
    print(mark(ipfs_connect_to_container(0)), "ipfs_api.find_peer")
    print(mark(docker_join_blockchain(0)), "join_blockchain")

    blockchain.add_block("DUMMY".encode())
    blockchain.add_block("Test1".encode())
    for _ in range(8):
        time.sleep(5)
        result = get_docker_latest_block_content(brenthy_dockers[0])
        success = result == "Test1"
        if success:
            break
    print(mark(success), "synchronised to peer on block creation")
    brenthy_dockers[0].stop()


def test_sync_on_join() -> None:
    """Test that blocks are synchronised to other nodes when joining."""
    time.sleep(2)
    brenthy_dockers[1].start()

    print(mark(ipfs_connect_to_container(1)), "ipfs_api.find_peer")
    print(mark(docker_join_blockchain(1)), "join_blockchain")

    for _ in range(8):
        polite_wait(5)
        print("Getting docker's latest block...")
        result = get_docker_latest_block_content(brenthy_dockers[1])
        success = result == "Test1"
        if success:
            break
    print(mark(success), "synchronised to peer on joining")


def test_sync_on_awake() -> None:
    """Test that blocks are synchronised to other nodes when coming online."""
    # test getting latest blocks on awaking
    brenthy_dockers[1].stop()
    blockchain.add_block("DUMMY".encode())
    blockchain.add_block("Test2".encode())
    polite_wait(10)
    brenthy_dockers[1].restart()
    for i in range(15):
        polite_wait(5)
        result = get_docker_latest_block_content(brenthy_dockers[1])
        success = result == "Test2"
        if success:
            break
    print(mark(success), "synchronised to peer on awaking")


def test_get_peers() -> None:
    """Test that we can get a list of connected nodes."""
    for container in brenthy_dockers:
        # container.start()
        container.restart()

    peers = blockchain.get_peers()

    # we're testing for if ANY docker peer is listed, because
    # IPFS' pubsub HTTP RPC system isn't reliable enough to test if ALL are
    peers_found = False
    for container in brenthy_dockers:
        if container.ipfs_id in peers:
            peers_found = True
    print(mark(peers_found), "get_peers")


def test_cleanup() -> None:
    """Test that all resources are cleaned up properly when shutting down."""
    blockchain.terminate()
    log.debug("test: deleting blockhain")
    walytis_beta_api.delete_blockchain(blockchain.blockchain_id)
    # Terminate Docker containers and our test brenthy instance in parallel
    termination_threads = []
    # start terminating docker containers
    for docker in brenthy_dockers:
        termination_threads.append(
            Thread(target=BrenthyDocker.stop, args=(docker,))
        )
        termination_threads[-1].start()
    # terminate our own brenthy instance
    stop_brenthy()
    # wair till all docker containers are terminated
    for thread in termination_threads:
        thread.join()


def run_tests() -> None:
    """Run all tests."""
    prepare()
    print("\nRunning tests for Walytis_Beta onboarding...")
    test_sync_block_creation()
    test_sync_on_join()
    test_sync_on_awake()
    test_get_peers()
    test_cleanup()
    test_threads_cleanup()


if __name__ == "__main__":
    run_tests()
