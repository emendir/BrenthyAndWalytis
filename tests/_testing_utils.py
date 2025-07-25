from tqdm import TMonitor, tqdm
from termcolor import colored as coloured
import time
import threading
import os
import sys
import pytest

from types import ModuleType
PROJECT_DIR=os.path.dirname(os.path.dirname(__file__))
brenthy_dir = os.path.join(
    PROJECT_DIR, "Brenthy"
)
blockchains_dir = os.path.join(brenthy_dir, "blockchains")
walytis_dir = os.path.join(blockchains_dir, "Walytis_Beta")
walytis_src_dir = os.path.join(blockchains_dir, "Walytis_Beta")
DEPLOYMENT_DIR=os.path.join(walytis_dir, "legacy_packages")
sys.path.insert(0, brenthy_dir)
sys.path.insert(0, blockchains_dir)
sys.path.insert(0, walytis_src_dir)
sys.path.insert(0, os.path.join(DEPLOYMENT_DIR, "walytis_beta_embedded"))
if True:
    # ensure IPFS is initialised via Walytis_Beta.networking, not walytis_beta_api
    from walytis_beta_tools._experimental.ipfs_interface import ipfs
    print("IPFS Peer ID:", ipfs.peer_id)

BREAKPOINTS = False # whether to open a PDB session if a test fails
PYTEST = True  # whether or not this script is being run by pytest instead of python


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

def assert_exception(exception, error_message, call, *args, **kwargs):
    """Run a function and check if it raises the specified error."""
    if PYTEST:
        with pytest.raises(exception, match=error_message):
            call(*args, **kwargs)
        return True
    else:
        try:
            call(*args, **kwargs)
        except Exception as e:
            if isinstance(e, exception) and error_message in str(e):
                return True
            raise e
        return False
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
        f"The module `{module.__name__}` has been loaded from an installion, "
        "not this source code!\n"
        f"Desired source dir: {source_path}\n"
        f"Loaded module path: {module_path}\n"
    )
    print(f"Using module {module.__name__} from {module_path}")
