"""Manages the installed blockchain types."""
# pylint: disable=global-statement

import os
from types import ModuleType

from brenthy_tools_beta import log, utils

# list of the blockchains we're running
blockchain_modules: list[ModuleType] = []
os.chdir(os.path.dirname(__file__))

BLOCKCHAIN_REQUIRED_MODULES = [
    ("__init__.py",),
    ("BLOCKCHAIN_TYPE_api", "BLOCKCHAIN_TYPE_api.py"),
]
IGNORED_FOLDERS = {"__pycache__"}


def run_blockchains() -> None:  # pylint: disable=unused-variable
    """Run all blockchain types."""
    # ask each blockchain module to load its blockchains
    for blockchain_module in load_blockchain_modules():
        blockchain_module.run_blockchains()


def load_blockchain_modules() -> list:
    """Load the installed blockchain types, ensuring they are valid."""
    global blockchain_modules
    blockchain_modules = []
    for blockchain_type in os.listdir("blockchains"):
        blockchain_path = os.path.join("blockchains", blockchain_type)
        # check if all the modules specified in BLOCKCHAIN_REQUIRED_MODULES
        # exist in the folder, if not skip this folder
        missing_modules = []
        for module_variants in BLOCKCHAIN_REQUIRED_MODULES:
            module_found = False
            for variant in module_variants:
                if os.path.exists(
                    os.path.join(
                        blockchain_path,
                        variant.replace(
                            "BLOCKCHAIN_TYPE", blockchain_type.lower()
                        ),
                    )
                ):
                    module_found = True
                    break
            if not module_found:
                missing_modules.append(module_variants)

        if missing_modules:
            if blockchain_type not in IGNORED_FOLDERS and os.path.isdir(
                blockchain_path
            ):
                log.warning(
                    f"Skipping loading of '{blockchain_type}' because it "
                    + "is missing some of the fields required by a "
                    + "blockchain type: "
                    + "; ".join(
                        [
                            " or ".join(list(variants))
                            for variants in missing_modules
                        ]
                    )
                )
            continue
        try:
            blockchain_module = utils.load_module_from_path(blockchain_path)
        except Exception as e:  # pylint:disable=broad-exception-caught
            log.error(f"Failed to load blockchain type {blockchain_type}\n{e}")
            continue
        blockchain_module.blockchain_type = blockchain_type
        blockchain_modules.append(blockchain_module)
    log.important(
        "Loaded blockchain modules: "
        f"{[module.blockchain_type for module in blockchain_modules]}"
    )
    return blockchain_modules


def terminate() -> None:  # pylint: disable=unused-variable
    """Shut down all blockchain types."""
    for module in blockchain_modules:
        module.terminate()
