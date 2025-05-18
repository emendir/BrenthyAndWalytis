
import os
import sys
import threading
import time
from types import ModuleType

from termcolor import colored as coloured
from tqdm import TMonitor, tqdm

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR=os.path.join(
    PROJ_DIR, "src"
)
EMBEDDED_DIR=os.path.join(
    PROJ_DIR, "legacy_packaging", "walytis_beta_embedded"
)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, EMBEDDED_DIR)

BREAKPOINTS = False
PYTEST = True  # whether or not this script is being run by pytest
USING_BRENTHY = False  # overridden to True in docker container
WE_ARE_IN_DOCKER=os.path.exists('/.dockerenv')

if WE_ARE_IN_DOCKER:
    USING_BRENTHY = True


def mark(success: bool, message: str, error: Exception | None = None) -> None:
    """Handle test results in a way compatible with and without pytest.

    Prints a check or cross and message depending on the given success.
    If pytest is running this test, an exception is thrown if success is False.

    Args:
        success: whether or not the test succeeded
        message: short description of the test to print
        error: Exception to raise/print in case of failure
    """
    if success:
        mark = coloured("✓", "green")
    else:
        mark = coloured("✗", "red")

    print(mark, message)
    if not success:
        if PYTEST:
            if error:
                raise error
            raise Exception(f'Failed at test: {message}')
        if error:
            print(str(error))
        if BREAKPOINTS:
            breakpoint()


def test_threads_cleanup() -> None:
    """Test that all threads have exited."""
    for i in range(2):
        polite_wait(5)
        threads = [
            x for x in threading.enumerate() if not isinstance(x, TMonitor)
        ]
        success = len(threads) == 1
        if success:
            break
    mark(success, "thread cleanup")
    if not success:
        [print(x) for x in threads]


def polite_wait(n_sec: int) -> None:
    """Wait for the given duration, displaying a progress bar."""
    # print(f"{n_sec}s patience...")
    for i in tqdm(range(n_sec), leave=False):
        time.sleep(1)


def assert_is_loaded_from_source(source_dir: str, module: ModuleType) -> None:
    """Assert a module is loaded from source code, not an installation.

    Asserts that the loaded module's source code is located within the given
    directory, regardless of whether it's file is located in that folder or is
    nested in subfolders.

    Args:
        source_dir: a directory in which the module's source should be
        module: the module to check
    """
    module_path = os.path.abspath(module.__file__)
    source_path = os.path.abspath(source_dir)
    assert (
        source_path in module_path
    ), (
        f"The module `{
            module.__name__}` has been loaded from an installion, not this "
        " source code!\n"
        f"Desired source dir: {source_path}\n"
        f"Loaded module path: {module_path}\n"
    )
    print(f"Using module {module.__name__} from {module_path}")


def terminate():
    walytis_beta_embedded.terminate()
    ipfs.terminate()
    
if True:
    print("USING_BRENTHY", USING_BRENTHY)
    # ensure IPFS is initialised via Walytis_Beta.networking, not walytis_beta_api
    if USING_BRENTHY:
        os.environ["USE_IPFS_NODE"] = "false"
        os.environ["WALYTIS_BETA_API_TYPE"] = "WALYTIS_BETA_BRENTHY_API"
    else:
        os.environ["USE_IPFS_NODE"] = "true"

    import walytis_beta_embedded
    from walytis_beta_tools._experimental.config import ipfs
    import walytis_beta_api
    import walytis_beta_tools
    assert_is_loaded_from_source(EMBEDDED_DIR, walytis_beta_embedded)
    assert_is_loaded_from_source(SRC_DIR, walytis_beta_api)
    assert_is_loaded_from_source(SRC_DIR, walytis_beta_tools)
    from brenthy_tools_beta import BrenthyNotRunningError

    if USING_BRENTHY:
        while True:
            try:
                walytis_beta_api.list_blockchain_names()
                break
            except BrenthyNotRunningError as e:
                print(e)
                print("Retrying to connect to brenthy...")
    else:
        walytis_beta_embedded.set_appdata_dir("./.blockchains")
        walytis_beta_embedded.run_blockchains()
    print("IPFS Peer ID:", ipfs.peer_id)
