"""Test that Walytis' core functionality works, quickly.

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

import _testing_utils
from test_walytis_beta import (
    stop_walytis,
    test_add_block,
    test_create_blockchain,
    test_create_invitation,
    test_delete_blockchain,
    test_list_blockchain_ids,
    test_list_blockchain_names,
    test_list_blockchains,
    test_list_blockchains_names_first,
    test_run_walytis,
    test_threads_cleanup,
)

NUMBER_OF_JOIN_ATTEMPTS = 10
# enable/disable breakpoints when checking intermediate test results
_testing_utils.BREAKPOINTS = True

# if you do not have any other important brenthy docker containers,
# you can set this to true to automatically remove unpurged docker containers
# after failed tests
DELETE_ALL_BRENTHY_DOCKERS = True


def run_tests() -> None:
    """Run all tests."""
    print("\nRunning quick tests for walytis_beta...")
    test_run_walytis()

    test_create_blockchain()
    test_add_block()
    test_create_invitation()

    test_list_blockchains()
    test_list_blockchains_names_first()
    test_list_blockchain_ids()
    test_list_blockchain_names()

    test_delete_blockchain()
    stop_walytis()
    test_threads_cleanup()


if __name__ == "__main__":
    _testing_utils.PYTEST = False
    run_tests()

    _testing_utils.terminate()
