import _testing_utils
from tqdm import tqdm
from func_monitoring import FuncLogger
from apply_decorators import decorate_class_method, decorate_module_functions, decorate_module_function
import pytest
import os

CLEAR=False


N_BLOCKS = 100
N_BLOCKCHAINS = 50
N_BLOCKS_PER_BLOCKCHAIN = 0


mon_ipfs = FuncLogger("brenthy_ipfs")
mon_brenthy = FuncLogger("brenthy")

# mon_ipfs.add_null_data()
# mon_brenthy.add_null_data()

if CLEAR:
    mon_ipfs.clear()
    mon_brenthy.clear()



if True:

    import run
    import ipfs_api
    # decorate_module_functions(mon_ipfs.track_time, ipfs_api)
    mon_ipfs.track_module_func(ipfs_api, "publish")
    mon_ipfs.track_module_func(ipfs_api, "predict_cid")
    mon_ipfs.track_module_func(ipfs_api, "download")
    mon_ipfs.track_module_func(ipfs_api, "read")
    mon_ipfs.track_module_func(ipfs_api, "pin")
    mon_ipfs.track_module_func(ipfs_api, "unpin")
    mon_ipfs.track_module_func(ipfs_api, "remove")
    mon_ipfs.track_module_func(ipfs_api, "pins")
    mon_ipfs.track_module_func(ipfs_api, "create_ipns_record")
    mon_ipfs.track_module_func(ipfs_api, "update_ipns_record_from_cid")
    mon_ipfs.track_module_func(ipfs_api, "update_ipns_record")
    mon_ipfs.track_module_func(ipfs_api, "resolve_ipns_key")
    mon_ipfs.track_module_func(ipfs_api, "download_ipns_record")
    mon_ipfs.track_module_func(ipfs_api, "read_ipns_record")
    mon_ipfs.track_module_func(ipfs_api, "get_ipns_record_validity")
    mon_ipfs.track_module_func(ipfs_api, "my_id")
    mon_ipfs.track_module_func(ipfs_api, "is_ipfs_running")
    mon_ipfs.track_module_func(ipfs_api, "my_multiaddrs")
    mon_ipfs.track_module_func(ipfs_api, "list_peers")
    mon_ipfs.track_module_func(ipfs_api, "list_peer_multiaddrs")
    mon_ipfs.track_module_func(ipfs_api, "get_peer_multiaddrs")
    mon_ipfs.track_module_func(ipfs_api, "connect_to_peer")
    mon_ipfs.track_module_func(ipfs_api, "find_peer")
    mon_ipfs.track_module_func(ipfs_api, "is_peer_connected")
    mon_ipfs.track_module_func(ipfs_api, "find_providers")
    mon_ipfs.track_module_func(ipfs_api, "create_tcp_listening_connection")
    mon_ipfs.track_module_func(ipfs_api, "create_tcp_sending_connection")
    mon_ipfs.track_module_func(ipfs_api, "close_all_tcp_connections")
    mon_ipfs.track_module_func(ipfs_api, "close_tcp_sending_connection")
    mon_ipfs.track_module_func(ipfs_api, "close_tcp_listening_connection")
    mon_ipfs.track_module_func(ipfs_api, "check_peer_connection")
    mon_ipfs.track_module_func(ipfs_api, "pubsub_publish")
    mon_ipfs.track_module_func(ipfs_api, "pubsub_subscribe")
    mon_ipfs.track_module_func(ipfs_api, "pubsub_peers")
    mon_ipfs.track_module_func(ipfs_api, "add_swarm_filter")
    mon_ipfs.track_module_func(ipfs_api, "rm_swarm_filter")
    mon_ipfs.track_module_func(ipfs_api, "get_swarm_filters")

    import blockchain_manager
    import walytis_beta_api
    from test_walytis_beta import stop_brenthy, test_run_brenthy
    from walytis_beta_api import Blockchain
    test_run_brenthy()

    walytis = [
        mod for mod in blockchain_manager.blockchain_modules
        if mod.__name__ == "Walytis_Beta"
    ][0]

    mon_brenthy.track_class_method(walytis.networking.Networking, "get_pubsub_peers")
    mon_brenthy.track_class_method(walytis.Blockchain, "create_block")
    mon_brenthy.track_module_func(walytis.walytis_beta, "create_blockchain")


_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=run
)
_testing_utils.assert_is_loaded_from_source(
    source_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    module=walytis_beta_api
)



def create_large_blockchain():
    print("Creating blockchain...")
    bc = Blockchain.create(app_name="mem_test")
    blockchain_id = bc.blockchain_id

    print("Adding some rather large blocks...")
    for i in tqdm(range(N_BLOCKS)):
        bc.add_block(bytearray([0]) * 100000, topics=["odd"])
    pytest.test_blockchains.append(bc)
    return bc




def create_many_blockchains():

    print("Creating a bunch of blockchains...")
    for i in tqdm(range(N_BLOCKCHAINS)):
        blockchain = Blockchain.create()
        pytest.test_blockchains.append(blockchain)
        for i in range(N_BLOCKS_PER_BLOCKCHAIN):
            blockchain.add_block(bytearray([0]) * 100000)
        for bc in pytest.test_blockchains:
            bc.add_block(bytearray([0]) * 100000)
            

def test_preparations():
    pytest.test_blockchains = []
    
from threading import Thread
def test_cleanup():
    threads = []
    for blockchain in pytest.test_blockchains:
        thr=Thread(target=blockchain.delete)
        thr.start()
        threads.append(thr)
    for thr in threads:
        thr.join()
    stop_brenthy()
    mon_ipfs.terminate()
    mon_brenthy.terminate()


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
