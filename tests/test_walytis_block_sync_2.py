import json
from time import sleep
import tempfile
import testing_utils
from test_walytis_beta import (
    stop_brenthy,

    test_run_brenthy,
    test_threads_cleanup,
)

import os
import shutil
import sys
import time

import ipfs_api
import pytest
import testing_utils
from brenthy_docker import BrenthyDocker, delete_containers, build_docker_image

from testing_utils import mark, test_threads_cleanup
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
    from walytis_beta_api import (
        Block, Blockchain, list_blockchain_names, delete_blockchain
    )
    import walytis_beta_api
    walytis_beta_api.log.PRINT_DEBUG = True
NUMBER_OF_JOIN_ATTEMPTS = 10
DOCKER_CONTAINER_NAME = "brenthy_tests_walytis"
REBUILD_DOCKER = True

# if you do not have any other important brenthy docker containers,
# you can set this to true to automatically remove unpurged docker containers
# after failed tests
DELETE_ALL_BRENTHY_DOCKERS = True
BLOCKCHAIN_NAME = "TestingBrenthyAppdata"
SYNC_DUR = 30
USE_SYSTEM_BRENTHY = False


MESSAGE_1 = "Hello there!"
MESSAGE_2 = "Gday!"
MESSAGE_3 = "Hi!"


def prepare() -> None:
    """Get everything needed to run the tests ready."""
    global brenthy_docker
    if DELETE_ALL_BRENTHY_DOCKERS:
        delete_containers(image="local/brenthy_testing",
                          container_name_substr="brenthy_tests_")

    if REBUILD_DOCKER:
        build_docker_image(verbose=False)
    false_id_path = os.path.join(
        walytis_beta_appdata.walytis_beta_appdata_dir, "FALSE_BLOCKCHAIN_ID"
    )
    if os.path.exists(false_id_path):
        shutil.rmtree(false_id_path)

    pytest.brenthy_docker_1 = BrenthyDocker(
        image="local/brenthy_testing",
        container_name=f"{DOCKER_CONTAINER_NAME}_1",
        auto_run=True
    )
    pytest.brenthy_docker_2 = BrenthyDocker(
        image="local/brenthy_testing",
        container_name=f"{DOCKER_CONTAINER_NAME}_2",
        auto_run=True
    )


def test_create_blockchain() -> None:
    """Test that we can create a Walytis blockchain."""
    if BLOCKCHAIN_NAME in list_blockchain_names():
        delete_blockchain(BLOCKCHAIN_NAME)
    pytest.blockchain = walytis_beta_api.Blockchain.create(
        BLOCKCHAIN_NAME,
        app_name="BrenthyTester",
        block_received_handler=None,
    )
    pytest.blockchain_id = pytest.blockchain.blockchain_id
    pytest.blockchain.add_block(MESSAGE_1.encode())
    appdata_path = pytest.blockchain.get_blockchain_data()
    print(mark(os.path.isfile(appdata_path)), "Got blockchain appdata.")
    pytest.appdata_cid = ipfs_api.publish(appdata_path)
    pytest.blockchain.terminate()


def docker_load_blockchain(bc_id: str, appdata_cid: str, ):
    download_tempdir = tempfile.mkdtemp()

    appdata_path = os.path.join(download_tempdir, "blockchain_data.zip")
    ipfs_api.download(appdata_cid, appdata_path)
    walytis_beta_api.join_blockchain_from_zip(
        bc_id, appdata_path, blockchain_name=BLOCKCHAIN_NAME
    )
    pytest.blockchain = Blockchain(bc_id)


def docker_1_part_1(bc_id: str, appdata_cid: str, ):
    docker_load_blockchain(bc_id, appdata_cid)
    pytest.blockchain.add_block(MESSAGE_2.encode())
    pytest.blockchain.add_block(MESSAGE_2.encode())
    pytest.blockchain.add_block(MESSAGE_2.encode())
    pytest.blockchain.terminate()


def docker_2_part_1(bc_id: str, appdata_cid: str, ):
    docker_load_blockchain(bc_id, appdata_cid)
    pytest.blockchain.add_block(MESSAGE_3.encode())
    pytest.blockchain.add_block(MESSAGE_3.encode())
    pytest.blockchain.add_block(MESSAGE_3.encode())
    pytest.blockchain.terminate()


def docker_1_part_2():
    pytest.blockchain = Blockchain(BLOCKCHAIN_NAME)
    print([block.content.decode()
          for block in pytest.blockchain.get_blocks() if "genesis" not in block.topics])
    pytest.blockchain.terminate()


DOCKER_CODE_PRELUDE = """
import os, sys
sys.path.append('/opt/Brenthy/tests/')
import pytest
import test_walytis_block_sync_2
"""
DOCKER_1_PART_1 = DOCKER_CODE_PRELUDE + """
test_walytis_block_sync_2.docker_1_part_1("BC_ID", "APPDATA_CID")
"""
DOCKER_2_PART_1 = DOCKER_CODE_PRELUDE + """
test_walytis_block_sync_2.docker_2_part_1("BC_ID", "APPDATA_CID")
"""
DOCKER_1_PART_2 = DOCKER_CODE_PRELUDE + """
test_walytis_block_sync_2.docker_1_part_2()
"""
DOCKER_2_PART_2 = DOCKER_1_PART_2


def test_block_sync():
    print("Testing blockchain sync")
    pytest.brenthy_docker_1.run_python_code(
        DOCKER_1_PART_1.replace("APPDATA_CID", pytest.appdata_cid).replace(
            "BC_ID", pytest.blockchain_id),
        print_output=False,
    )
    pytest.brenthy_docker_1.stop()

    pytest.brenthy_docker_2.run_python_code(
        DOCKER_2_PART_1.replace("APPDATA_CID", pytest.appdata_cid).replace(
            "BC_ID", pytest.blockchain_id),
        print_output=False,
    )
    pytest.brenthy_docker_2.stop()

    pytest.brenthy_docker_1.start()
    pytest.brenthy_docker_2.start()
    sleep(SYNC_DUR)
    output = pytest.brenthy_docker_1.run_python_code(
        DOCKER_1_PART_2, print_output=False
    )
    last_line = output.split("\n")[-1].strip()
    blocks_content = json.loads(last_line.replace("'", '"'))
    print(mark(
        blocks_content == [MESSAGE_1, MESSAGE_2, MESSAGE_2,
                           MESSAGE_2, MESSAGE_3, MESSAGE_3, MESSAGE_3],
        
    ), "docker_1 synchronised!")
    output = pytest.brenthy_docker_2.run_python_code(
        DOCKER_2_PART_2, print_output=False
    )
    last_line = output.split("\n")[-1].strip()
    blocks_content = json.loads(last_line.replace("'", '"'))
    print(mark(
        blocks_content == [MESSAGE_1, MESSAGE_2, MESSAGE_2,
                           MESSAGE_2, MESSAGE_3, MESSAGE_3, MESSAGE_3],
        ),
        "docker_2 synchronised!"
    )


def cleanup():
    pytest.brenthy_docker_1.delete()
    pytest.brenthy_docker_2.delete()


def run_tests() -> None:
    """Run all tests."""
    print("\nRunning tests for Walytis joining & block sync 2...")
    prepare()
    if not USE_SYSTEM_BRENTHY:
        test_run_brenthy()

    test_create_blockchain()

    test_block_sync()
    if not USE_SYSTEM_BRENTHY:
        stop_brenthy()
    test_threads_cleanup()
    cleanup()


if __name__ == "__main__":
    # enable/disable breakpoints when checking intermediate test results
    testing_utils.BREAKPOINTS = True
    run_tests()
