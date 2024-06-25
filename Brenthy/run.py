"""The entry point for Brenthy Core.

- checks installation and update status
- runs various blockchain types
"""

# pylint: disable=global-statement
import os
import sys
import traceback
from importlib import reload

from app_data import logs_dir
from install import (
    InstallationResult,
    am_i_installed,
    install,
    try_install_python_modules,
)

if True:  # pylint: disable=using-constant-test
    os.chdir(os.path.dirname(__file__))
    from brenthy_tools_beta import log
    from brenthy_tools_beta.versions import BRENTHY_CORE_VERSION
    # log.set_print_level("Info")
# install required python modules if they don't yet exist
try_install_python_modules()

# from subprocess import Popen, PIPE
if str(sys.version)[0] != "3":  # pylint: disable=magic-value-comparison
    print("Use Python3!")
    input()
    sys.exit()
print(__file__)


print(f"Brenthy {BRENTHY_CORE_VERSION}")

TRY_INSTALL = True
DATA_DIR = ""
CHECK_UPDATES = True

api_terminal = None
blockchain_manager = None
update = None


def run_brenthy() -> None:
    """Run Brenthy."""
    global api_terminal
    global blockchain_manager
    global update
    global bt_endpoints
    global walytis_beta_api
    global TRY_INSTALL
    global CHECK_UPDATES
    global DATA_DIR
    # First things first: get logging working
    log.LOG_DIR = logs_dir
    log.LOG_FILENAME = "Brenthy.log"
    log.LOG_ARCHIVE_DIRNAME = ".log_archive"
    log.add_empty_line()
    log.important("Starting up Brenthy...")
    try:
        if "--dont-install" in sys.argv:
            TRY_INSTALL = False
        if "--dont-update" in sys.argv:
            CHECK_UPDATES = False
        if "--print-log-level" in sys.argv:
            log_level = sys.argv[sys.argv.index("--print-log-level") + 1]
            log.set_print_level(log_level)
        if "--data-dir" in sys.argv:
            data_dir = sys.argv[sys.argv.index("--data-dir") + 1]
            print("DATA_DIR", data_dir)
            if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
                error_message = (
                    "The value of `data-dir` must be an existing directory. "
                    f"'{data_dir}' is not."
                )
                log.fatal(error_message)
                raise ValueError(error_message)
            DATA_DIR = data_dir
    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal(
            "Failed to parse the Brenthy execution arguments, exiting Brenthy."
        )
        sys.exit()

    # check if we should install ourselves on the operating system
    exit_brenthy = False
    try:
        if TRY_INSTALL:
            if not am_i_installed():
                result = install(data_dir=DATA_DIR)
                match result:
                    case InstallationResult.INSTALLED:
                        log.important("Installation finished!")
                        exit_brenthy = True
                    case InstallationResult.FAILED:
                        log.important("Installation not possible/failed")
                        exit_brenthy = True
                    case InstallationResult.DECLINED:
                        log.important("Installation declined by user")
        if "--install-dont-run" in sys.argv:
            log.important(
                "Exiting because --install-dont-run is specified."
            )
            exit_brenthy = True
    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal(
            "Failed while checking Brenthy installation status or trying to "
            "install, exiting Brenthy."
        )
        exit_brenthy = True
    if exit_brenthy:
        sys.exit()

    try:
        # Wait till IPFS comes online
        import ipfs_api  # pylint: disable=import-outside-toplevel

        try:
            ipfs_api.wait_till_ipfs_is_running(timeout_sec=5)
        except TimeoutError:
            log.warning("IPFS isn't running. Waiting for IPFS to start...")
            ipfs_api.wait_till_ipfs_is_running()
            log.warning("IPFS running now, starting Brenthy now...")

    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal(
            "Not all prerequisite libraries are installed, exiting Brenthy."
        )
        sys.exit()

    try:
        # pylint: disable=import-outside-toplevel
        # pylint: disable=redefined-outer-name
        import api_terminal
        import blockchain_manager  # Running the core of Brenthy
        import update
        from blockchains.Walytis_Beta import walytis_beta_api
        from blockchains.Walytis_Beta.walytis_beta_api import walytis_beta_interface

        from brenthy_tools_beta import bt_endpoints
        bt_endpoints.initialise()
        walytis_beta_interface.log.PRINT_DEBUG = not am_i_installed() or update.TESTING

        log.important("Starting up communication with applications...")
        api_terminal.load_brenthy_api_protocols()
    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal("Error initialising Brenthy, exiting.")
        sys.exit()

    try:
        log.important("Running blockchains...")
        blockchain_manager.run_blockchains()
        # re-enable log.PRINT_DEBUG again, as run_blockchains() disables it again
        walytis_beta_interface.log.PRINT_DEBUG = not am_i_installed() or update.TESTING
    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal("Error running blockchains, exiting.")
        sys.exit()

    try:
        # start listening to requests by topic programs
        api_terminal.start_listening_for_requests()
    except:  # pylint: disable=bare-except
        log.fatal(traceback.format_exc())
        log.fatal("Error starting api_terminal, shutting down...")
        stop_brenthy()
        log.fatal("Error starting api_terminal, exiting.")
        sys.exit()

    try:
        if CHECK_UPDATES:
            update.check_on_updates()
    except:  # pylint: disable=bare-except
        log.error("Error checking on updates.")


def stop_brenthy() -> None:
    """Stop Brenthy-Core."""
    log.important("Stopping Brenthy...")
    try:
        api_terminal.terminate()
    except:  # pylint: disable=bare-except
        log.error("Error shutting down api_terminal.")

    try:
        blockchain_manager.terminate()
    except:  # pylint: disable=bare-except
        log.error("Error shutting down blockchain-types manager.")

    try:
        update.terminate_updater()
    except:  # pylint: disable=bare-except
        log.error("Error shutting down Brenthy-updater.")

    try:
        bt_endpoints.terminate()
    except:  # pylint: disable=bare-except
        log.error("Error shutting down bt_endpoints.")
    reload(api_terminal)
    reload(blockchain_manager)
    reload(update)


def restart_brenthy() -> None:  # pylint: disable=unused-variable
    """Restart Brenthy."""
    log.important("Restarting Brenthy...")
    stop_brenthy()
    run_brenthy()


if __name__ == "__main__":
    import atexit

    run_brenthy()
    print("Press Ctrl+C to stop Brenthy.")
    atexit.register(stop_brenthy)
