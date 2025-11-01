from time import sleep
import sys
from threading import Thread
import _testing_utils
from tqdm import tqdm
from func_monitoring import FuncLogger
from apply_decorators import (
    decorate_class_method,
    decorate_module_functions,
    decorate_module_function,
    decorate_class_methods,
)
import pytest
import os

CLEAR = False


N_BLOCKS = 500
N_BLOCKCHAINS = 500
N_BLOCKS_PER_BLOCKCHAIN = 500
BLOCK_SIZE_BYTES = 100000

mon_ipfs = FuncLogger("brenthy_ipfs")
mon_brenthy = FuncLogger("brenthy")

# mon_ipfs.add_null_data()
# mon_brenthy.add_null_data()

if CLEAR:
    mon_ipfs.clear()
    mon_brenthy.clear()


def stop_brenthy() -> None:
    """Stop Brenthy-Core."""
    run.stop_brenthy()


def test_run_brenthy() -> None:
    """Test that we can run Brenthy-Core."""
    run.TRY_INSTALL = False
    run.log.set_print_level("important")
    try:
        run.run_brenthy()
    except Exception as e:
        print(e)
        sys.exit()


if True:
    import run
    from walytis_beta_tools._experimental.ipfs_interface import ipfs

    mon_brenthy.track_class_methods(ipfs)

    import blockchain_manager
    import walytis_beta_api
    from walytis_beta_api import Blockchain

    test_run_brenthy()

    walytis = blockchain_manager.blockchain_modules[
        "Walytis_Beta"
    ].walytis_beta

    mon_brenthy.track_class_method(walytis.networking.Networking, "get_peers")
    mon_brenthy.track_class_method(walytis.Blockchain, "create_block")
    mon_brenthy.track_class_method(walytis.Blockchain, "read_block")
    mon_brenthy.track_module_func(walytis.walytis_beta, "create_blockchain")
    mon_brenthy.track_class_method(walytis_beta_api.Blockchain, "add_block")
    sleep(5)

_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=run,
)
_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=walytis_beta_api,
)


def create_large_blockchain():
    print("Creating blockchain...")
    bc = Blockchain.create(app_name="mem_test")
    blockchain_id = bc.blockchain_id

    print("Adding some rather large blocks...")
    for i in tqdm(range(N_BLOCKS)):
        bc.add_block(bytearray([0]) * BLOCK_SIZE_BYTES, topics=["odd"])
    pytest.test_blockchains.append(bc)
    return bc


def create_many_blockchains():
    print(
        f"Creating {N_BLOCKCHAINS} blockchains, "
        f"each with {N_BLOCKS_PER_BLOCKCHAIN} blocks "
        f"of size {BLOCK_SIZE_BYTES} bytes"
    )
    for i in tqdm(range(N_BLOCKCHAINS)):
        blockchain = Blockchain.create()
        pytest.test_blockchains.append(blockchain)
        for i in range(N_BLOCKS_PER_BLOCKCHAIN):
            blockchain.add_block(bytearray([0]) * BLOCK_SIZE_BYTES)
        for bc in pytest.test_blockchains:
            bc.add_block(bytearray([0]) * BLOCK_SIZE_BYTES)
        for block in bc.get_blocks():
            _ = block.content


def test_preparations():
    pytest.test_blockchains = []


def test_cleanup():
    threads = []
    for blockchain in pytest.test_blockchains:
        thr = Thread(target=blockchain.delete)
        thr.start()
        threads.append(thr)
    for thr in threads:
        thr.join()
    stop_brenthy()
    mon_ipfs.terminate()
    mon_brenthy.terminate()


def run_tests():
    test_preparations()

    # bc = create_large_blockchain()
    # print("Getting peers")
    # for i in range(50):
    #     bc.get_peers()

    create_many_blockchains()

    print("Cleaning up...")
    test_cleanup()


if __name__ == "__main__":
    run_tests()
