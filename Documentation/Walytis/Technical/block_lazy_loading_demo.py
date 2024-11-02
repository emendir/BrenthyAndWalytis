"""This script demonstrates the time a memory costs and savings
involved in the lazy block loading system for access to block information
in walytis_beta_api.
"""

print("Make sure Brenthy is running with PyPy, not CPython.")

from walytis_beta_api import Blockchain, Block
import psutil
from tqdm import tqdm
from datetime import datetime, UTC


def get_used_memory_mb():
    """Get the amount of memory used by this program in mibibytes"""
    return psutil.Process().memory_info().rss // 1024 // 1024


def measure_time(func, *args):
    starttime = datetime.now(UTC)
    func(*args)
    duration = (datetime.now(UTC) - starttime)
    return duration.total_seconds()


print("Creating blockchain...")
bc = Blockchain.create(app_name="mem_test")
blockchain_id = bc.blockchain_id


print("Adding some rather large blocks...")
for i in tqdm(range(100)):
    bc.add_block(bytearray([0]) * 100000, topics=["odd"])
bc.terminate()


print("Demonstrating Lazy Block Loading")
bc = Blockchain(blockchain_id)

# load the latest five blocks' metadata only


def read_blocks_metadata(percentage=100):
    """Access the block metadata for the given percentage of blocks"""
    max_count = bc.get_num_blocks() * percentage / 100
    counter = 0
    for block in bc.get_blocks(reverse=True):
        _ = block
        counter += 1
        if counter > max_count:
            break   # break out of loop to stop loading the rest of the blocks' metadata


def get_first_block_stored_data():
    return dict.__getitem__(bc._blocks, bc.get_block_ids()[0]).__class__

print(
    "Stored block value before accessing:",  # None
    get_first_block_stored_data()
)

print("Accessing Block Metadata:")
print(
    "Accessing last 10 blocks:        ",  # 0.000169s
    measure_time(read_blocks_metadata, 10), "seconds"
)
print(
    "Accessing last 100 blocks:       ",  # 0.000774s
    measure_time(read_blocks_metadata, 100), "seconds"
)
print(
    "Accessing last 100 blocks again: ",  # 0.000072s
    measure_time(read_blocks_metadata, 100), "seconds"
)

print(
    "Stored block value after accessing: ",  # BlockLazilyLoaded object
    get_first_block_stored_data()
)


def read_blocks_content():
    for block in bc.get_blocks():
        _ = block.content


print(
    "Memory usage:                        ",  # 41 MiB
    get_used_memory_mb(), "MiB"
)

print(
    "Accessing 100 blocks' content:       ",  # 0.6846s
    measure_time(read_blocks_content), "seconds"
)
print(
    "Memory usage:                        ",  # 61 MiB
    get_used_memory_mb(), "MiB"
)
print(
    "Accessing 100 blocks' content again :",  # 0.000102s
    measure_time(read_blocks_content), "seconds"
)
print(
    "Memory usage:                        ",  # 61 MiB
    get_used_memory_mb(), "MiB"
)


bc.terminate()
