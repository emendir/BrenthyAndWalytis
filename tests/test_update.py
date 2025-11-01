"""Tests that Brenthy Core's automatic update system works."""


# if you do not have any other important brenthy docker containers,
# you can set this to true to automatically remove unpurged docker containers
# after failed tests
DELETE_ALL_BRENTHY_DOCKERS = True
DOCKER_CONTAINER_NAME = "brenthy_tests_update"
REBUILD_DOCKER = True
# enable/disable breakpoints when checking intermediate test results
BREAKPOINTS = True
if True:
    import os
    import sys

    sys.path.append(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "publisher")
    )

    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )

    sys.path.insert(0, brenthy_dir)
    import run
    import publish_brenthy_updates  # pylint: disable=import-error
    
    import shutil
    import time

    from _testing_utils import ipfs
    import pytest

    import _testing_utils
    from brenthy_docker import BrenthyDocker, delete_containers, build_docker_image
    from update import get_walytis_appdata_dir
    from _testing_utils import mark, polite_wait, test_threads_cleanup
    
    _testing_utils.BREAKPOINTS = BREAKPOINTS

test_upd_blck_path = ""
brenthy_docker: BrenthyDocker

DELAY=90

def prepare() -> None:
    """Get everything needed to run the tests ready."""
    global test_upd_blck_path
    if DELETE_ALL_BRENTHY_DOCKERS:
        delete_containers(
            image="local/brenthy_testing",
            container_name_substr="brenthy"
        )
    if REBUILD_DOCKER:

        build_docker_image(verbose=False)
    run.TRY_INSTALL = False
    run.log.set_print_level("important")
    run.run_brenthy()
    upd_blck_path = os.path.join(get_walytis_appdata_dir(), "BrenthyUpdates")
    test_upd_blck_path = os.path.join(
        get_walytis_appdata_dir(), "BrenthyUpdatesTEST"
    )
    run.stop_brenthy()
    if os.path.exists(upd_blck_path):
        shutil.rmtree(upd_blck_path)
    if os.path.exists(test_upd_blck_path):
        shutil.rmtree(test_upd_blck_path)
    os.makedirs(test_upd_blck_path)
    # shutil.copytree(upd_blck_path, test_upd_blck_path)
    shutil.unpack_archive(
        os.path.join("..", "Brenthy", "InstallScripts", "BrenthyUpdates.zip"),
        test_upd_blck_path,
        "zip",
    )
    run.restart_brenthy()


def stop_brenthy() -> None:
    """Stop Brenthy-Core."""
    run.stop_brenthy()


def run_docker() -> None:
    """Run this test's docker container."""
    global brenthy_docker
    print("Creating docker image...")
    brenthy_docker = BrenthyDocker(
        image="local/brenthy_testing",
        container_name=DOCKER_CONTAINER_NAME
    )
    print("Created docker image!")
    time.sleep(10)


def get_docker_brenthy_version() -> str:
    """Get this test's docker container's running Brenthy-Core version."""
    return brenthy_docker.run_python_code(
        "import brenthy_tools_beta;"
        "print(brenthy_tools_beta.get_brenthy_version_string())",
        print_output=False
    ).split("\n")[-1]


def get_docker_walytis_beta_version() -> str:
    """Get this test's docker container's running Walytis-Core version."""
    return brenthy_docker.run_python_code(
        "import walytis_beta_api;"
        "print(walytis_beta_api.get_walytis_beta_version_string())",
        print_output=False
    ).split("\n")[-1]


# print("Starting tests...")


def test_find_peer() -> None:
    """Test that we are connected to the Brenthy docker container via IPFS."""
    success = False
    for _ in range(5):
        success = ipfs.peers.find(brenthy_docker.ipfs_id)
        if success:
            break

    mark(success, "ipfs.peers.find")

def test_walytis_beta_update() -> None:
    """Test that updating Walytis_Beta works."""
    # allow docker filesystem to consolidate after renaming updates blockchain
    # to avoid errors when copying Brenthy update folders
    brenthy_docker.restart()

    brenthy_version_1 = get_docker_brenthy_version()
    walytis_beta_version_1 = get_docker_walytis_beta_version()
    publish_brenthy_updates.publish_release(testing_walytis_beta_update=True)
    polite_wait(DELAY)
    brenthy_docker.restart()
    print("Reinstalling walytis_beta_api")
    brenthy_docker.run_shell_command(
        "rm -r /opt/Brenthy/Brenthy/blockchains/Walytis_Beta/build;",
        print_output=False, ignore_errors=True
    )
    brenthy_docker.run_shell_command(
        "rm -r /opt/Brenthy/Brenthy/blockchains/Walytis_Beta/*.egg-info;",
        print_output=False, ignore_errors=True
    )
    brenthy_docker.run_shell_command(
        "python3 -m pip install --break-system-packages /opt/Brenthy/Brenthy/blockchains/Walytis_Beta",
        print_output=False
    )
    walytis_beta_version_2 = get_docker_walytis_beta_version()
    brenthy_version_2 = get_docker_brenthy_version()
    
    mark((walytis_beta_version_2 == "9999" + walytis_beta_version_1),
        f"Walytis update {(walytis_beta_version_1, walytis_beta_version_2)}",
    )
    
    mark((brenthy_version_2 == brenthy_version_1),
        "Walytis_Beta update Brenthy version still the same",
        # (brenthy_version_1, brenthy_version_2),
    )


def test_brenthy_update() -> None:
    """Test that Brenthy-Core udpates are installed."""
    version_1 = get_docker_brenthy_version()
    publish_brenthy_updates.publish_release(testing_brenthy_update=True)
    polite_wait(DELAY)
    brenthy_docker.restart()
    # breakpoint()
    version_2 = get_docker_brenthy_version()
    mark((version_2 == "9999" + version_1),
        f"Brenthy update {(version_1, version_2)}",
    )


@pytest.fixture(scope="session", autouse=True)
def cleanup(request: pytest.FixtureRequest | None = None) -> None:
    """Clean up after running tests with PyTest."""
    brenthy_docker.stop()


def run_tests() -> None:
    """Run all tests."""
    prepare()
    print("\nRunning tests for update system...")
    run_docker()
    print("\nFinding peer...")
    test_find_peer()
    print("\nPreparing update...")
    test_walytis_beta_update()
    test_brenthy_update()

    brenthy_docker.stop()
    stop_brenthy()
    test_threads_cleanup()
    shutil.rmtree(test_upd_blck_path)


if __name__ == "__main__":
    run_tests()
