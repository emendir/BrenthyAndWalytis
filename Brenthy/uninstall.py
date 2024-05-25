"""The machinery for uninstalling Brenthy."""

import os
import platform
import sys

from install import _is_systemctl_installed


def uninstall() -> bool:
    """Uninstall Brenthy."""
    install_dir = "/opt/Brenthy"
    data_dir = "/opt/Brenthy/BlockchainData"

    # if OS is linux and systemctl is installed
    if platform.system().lower() == "linux" and _is_systemctl_installed():
        if not ask_user_uninstall():
            return False
        print("Enter your root password, if requested.")
        print("To cancel uninstallation, press Ctrl+D.")
        exit_code = os.system(
            "sudo su -c './InstallScripts/uninstall_brenthy_linux_systemd.sh "
            f"{install_dir} {data_dir} {sys.executable}'"
        )
        linux_uninstall_ipfs()
        return exit_code == 0
    return False


def ask_user_uninstall() -> bool:
    """Ask the user whether they want to uninstlal Brenthy."""
    # print in yellow/orange
    print("\033[93m" "Are you sure you want to uninstall Brenthy?" "\033[0m")
    return input("(y/n): ").lower() in {"y", "yes"}


def linux_uninstall_ipfs() -> None:
    """TODO: Uninstall IPFS."""
    # TODO
    print("Uninstalling IPFS not yet supported.")


if __name__ == "__main__":
    uninstall()
