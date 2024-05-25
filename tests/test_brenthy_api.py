"""Test that Brenthy runs and basic BrenthyAPI communication works.

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

import testing_utils
from testing_utils import mark, test_threads_cleanup

if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    import run
    from brenthy_tools_beta import brenthy_api
    # brenthy_api.PRINT_LOG = True

# enable/disable breakpoints when checking intermediate test results
testing_utils.BREAKPOINTS = True


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
        print(mark(False), "Failed to run Brenthy")
        print(e)
        sys.exit()


def test_get_brenthy_version() -> None:
    """Test that we can communicate with Brenthy-Core via BrenthyAPI."""
    try:
        version = brenthy_api.get_brenthy_version()
        print(mark(True), f"get_brenthy_version: {version}")
    except Exception as e:
        print(mark(False), "get_brenthy_version")
        print(e)
        sys.exit()


def run_tests() -> None:
    """Run all tests."""
    print("\nRunning tests for BrenthyAPI...")
    test_run_brenthy()
    test_get_brenthy_version()

    stop_brenthy()
    test_threads_cleanup()


if __name__ == "__main__":
    run_tests()
