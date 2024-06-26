"""The machinery for installing Brenthy."""

import os
import platform
import sys
from enum import Enum
from subprocess import PIPE, Popen

from brenthy_tools_beta.utils import get_file_owner

INSTALL_DIR = "/opt/Brenthy"
DEF_DATA_DIR = "/opt/Brenthy/BlockchainData"


def am_i_installed() -> bool:  # pylint: disable=unused-variable
    """Check if the running Brenthy instance is installed."""
    return get_file_owner(os.path.abspath(__file__)) == "brenthy"


class InstallationResult(Enum):
    """The result type for installation attempts."""

    INSTALLED = 1
    FAILED = 2
    DECLINED = 3


def install(data_dir: str = DEF_DATA_DIR) -> InstallationResult:
    """Install Brenthy.

    Args:
        data_dir (str): user-defined custom path to store blockchain data
    Returns:
        InstallationResult: whether the installation succeeded, failed, or was
                            declined
    """
    if not data_dir:
        data_dir = DEF_DATA_DIR
    elif data_dir != DEF_DATA_DIR:
        print(f"Using custom Brenthy data directory: {data_dir}")

    # if OS is linux and systemctl is installed
    if platform.system().lower() == "linux" and _is_systemctl_installed():
        # if no explicit install arguments were passed
        if not ("--install-dont-run" in sys.argv or "--install" in sys.argv):
            # ask user if they want to install Brenthy
            if not ask_user_install():
                return InstallationResult.DECLINED

        if os.path.exists("we_are_in_docker"):
            # installation on docker ubuntu
            exit_code = os.system(
                "bash ./InstallScripts/install_brenthy_linux_systemd.sh "
                f"{INSTALL_DIR} {data_dir} {sys.executable} "
                f"{'--install-dont-run' not in sys.argv}"
            )
        else:
            # installation on normal ubuntu
            linux_install_ipfs()

            print("To install Brenthy, enter your root password here.")
            print("To cancel installation, press Ctrl+D.")
            exit_code = os.system(
                "sudo su -c './InstallScripts/install_brenthy_linux_systemd.sh"
                f" {INSTALL_DIR} {data_dir} {sys.executable} "
                f"{'--install-dont-run' not in sys.argv}'"
            )

        if exit_code == 0:  # whether or not shell script exited normally
            return InstallationResult.INSTALLED

        return InstallationResult.FAILED

    # automatic installation not supported on this system
    return InstallationResult.FAILED


def uninstall() -> bool:  # pylint: disable=unused-variable
    """Uninstall Brenthy."""
    exit_code = os.system(
        "sudo su -c './InstallScripts/uninstall_brenthy_linux_systemd.sh "
        f"{INSTALL_DIR} {DEF_DATA_DIR} {sys.executable}'"
    )
    return exit_code == 0


def ask_user_install() -> bool:
    """Ask user if they want to install Brenthy."""
    # print in yellow/orange
    print("\033[93m" "Brenthy> Can I live here? Let's install me!" "\033[0m")
    print(
        "Installing allows Brenthy to update itself and automatically run on "
        "system startup."
    )
    return input("Install? (y/n):").lower() in {"y", "yes"}


def linux_install_ipfs() -> None:
    """Install IPFS."""
    if not _is_ipfs_installed():
        print("You don't seem to have IPFS installed.")
        if not ("--install-dont-run" in sys.argv or "--install" in sys.argv):
            if input(
                "Would you like me to install and configure it for you? (y/n):"
            ).lower() in {"y", "yes"}:
                return
        print(
            "Enter your user password to install IPFS, press Ctrl+D to skip."
        )
        os.system(
            "sudo su -c './InstallScripts/install_ipfs_linux_systemd.sh'"
        )


def _is_systemctl_installed() -> bool:
    """Check if systsmd is installed."""
    try:
        Popen(["systemctl", "--version"], shell=False, stdout=PIPE)
        return True
    except:  # pylint: disable=bare-except
        return False


def _is_ipfs_installed() -> bool:
    """Check if IPFS is installed."""
    try:
        Popen(["ipfs", "--version"], shell=False, stdout=PIPE)
        return True
    except:  # pylint: disable=bare-except
        return False


def try_install_python_modules() -> None:  # pylint: disable=unused-variable
    """Try install the python modules which."""
    requirements_path = os.path.join(
        os.path.dirname(__file__), "requirements.txt"
    )
    os.system(f"{sys.executable} -m pip -qq install -r {requirements_path}")


if __name__ == "__main__":
    install()
