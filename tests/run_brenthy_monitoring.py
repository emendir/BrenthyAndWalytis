import os

import _testing_utils
import func_monitoring
import pytest
import run
import walytis_beta_api
from apply_decorators import decorate_class_method
from func_monitoring import track_time
from test_walytis_beta import stop_brenthy, test_run_brenthy
from tqdm import tqdm
from walytis_beta_api import Blockchain

_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=run
)
_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=walytis_beta_api
)


def demo_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print("Decorator was here!")
        return result

    return wrapper


def setup_func_monitoring():
    import blockchain_manager
    walytis = [
        mod for mod in blockchain_manager.blockchain_modules
        if mod.__name__ == "Walytis_Beta"
    ][0]

    decorate_class_method(
        track_time, walytis.networking.Networking, "get_pubsub_peers")


N_BLOCKS = 100


def create_large_blockchain():
    print("Creating blockchain...")
    bc = Blockchain.create(app_name="mem_test")
    blockchain_id = bc.blockchain_id

    print("Adding some rather large blocks...")
    for i in tqdm(range(N_BLOCKS)):
        bc.add_block(bytearray([0]) * 100000, topics=["odd"])
    pytest.test_blockchains.append(bc)
    return bc


N_BLOCKCHAINS = 10


def create_many_blockchains():

    print("Creating a bunch of blockchains...")
    for i in tqdm(range(N_BLOCKCHAINS)):
        blockchain = Blockchain.create()
        pytest.test_blockchains.append(blockchain)
        blockchain.add_block(bytearray([0]) * 100000)


def test_preparations():

    pytest.test_blockchains = []

    test_run_brenthy()
    setup_func_monitoring()


def test_cleanup():
    for blockchain in pytest.test_blockchains:
        blockchain.delete()
    stop_brenthy()


def run_tests():
    test_preparations()

    bc = create_large_blockchain()
    print("Getting peers")
    for i in range(50):
        bc.get_peers()

    create_many_blockchains()

    print("Cleaning up...")
    test_cleanup()


if __name__ == "__main__":
    run_tests()
    func_monitoring.terminate()
