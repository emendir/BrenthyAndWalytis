"""The machinery for Publishing new releases of the blockchain."""

import json
import os
import shutil
import sys
import tempfile
from getpass import getpass

from cryptem import Crypt

publisher_public_key = "0459f93b7e8c77ec5daad9e2625ef5421028a8bcc3f158ce5e5085e1fde012e4a943a97446574d92f4330ce74c059dd4f66e78313021b8a3cdb0af141d58a70d0c"
crypt: Crypt

TESTING_BRENTHY = False
TESTING_WALYTIS_BETA = False

PREFERRED_SIG_ALGORITHM = "EC-secp256k1.SHA256"


def unlock_publisher() -> None:
    """Ask user for the publishing password."""
    global crypt
    crypt = Crypt(password=getpass("enter password for Brenthy releases:"))


unlock_publisher()

while crypt.public_key != publisher_public_key:
    unlock_publisher()

if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    from blockchains.Walytis_Beta.networking import ipfs
    from blockchain_manager import load_blockchain_modules
    from brenthy_tools_beta import log
    from brenthy_tools_beta.utils import (
        bytes_to_string,
        load_module_from_path,
    )
    from brenthy_tools_beta.versions import BRENTHY_CORE_VERSION

    brenthy_version = BRENTHY_CORE_VERSION
    from blockchains.Walytis_Beta import walytis_beta_api

    walytis_beta_version = walytis_beta_api.WALYTIS_BETA_CORE_VERSION

    walytis_beta_api = load_module_from_path(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Brenthy",
            "blockchains",
            "Walytis_Beta",
            "walytis_beta_api",
        )
    )
    from walytis_beta_api.walytis_beta_interface import WALYTIS_BETA


def publish_release(
    testing_brenthy_update: bool = False,
    testing_walytis_beta_update: bool = False,
) -> None:
    """Package and publish the current source code as a Brenthy release."""
    global TESTING_BRENTHY
    global TESTING_WALYTIS_BETA
    global brenthy_version
    global walytis_beta_version
    TESTING_BRENTHY = testing_brenthy_update
    TESTING_WALYTIS_BETA = testing_walytis_beta_update

    # get list of blockchains and their versions
    blockchain_versions = [
        {"blockchain_type": module.blockchain_type, "version": module.version}
        for module in load_blockchain_modules().values()
    ]
    log.important("Preparing to publish release...")
    if TESTING_BRENTHY or TESTING_WALYTIS_BETA:
        log.important("PUBLISH - TESTING ---- TESTING ----")
        update_blockchain = walytis_beta_api.Blockchain(
            "BrenthyUpdatesTEST",
            app_name="BrenthyPublisher",
        )
        if TESTING_BRENTHY:
            brenthy_version = tuple(
                [int("9999" + str(brenthy_version[0])), *brenthy_version[1:]]
            )
        elif TESTING_WALYTIS_BETA:
            walytis_beta_version = tuple(
                [
                    int("9999" + str(walytis_beta_version[0])),
                    *walytis_beta_version[1:],
                ]
            )
            for i, blockchain in enumerate(blockchain_versions):
                if blockchain["blockchain_type"] == WALYTIS_BETA:
                    blockchain_versions[i]["version"] = walytis_beta_version
    else:
        update_blockchain = walytis_beta_api.Blockchain(
            "BrenthyUpdates",
            app_name="BrenthyPublisher",
        )

    log.important("Publishing Brenthy on IPFS...")
    ipfs_cid = publish_project_on_ipfs()

    # compose block content for publishing release info on BrenthyUpdates
    block_content = {
        "brenthy_version": brenthy_version,
        "blockchains": blockchain_versions,
        "ipfs_cid": ipfs_cid,
        "signature_algorithm": PREFERRED_SIG_ALGORITHM,
    }

    # sign block content
    signature = crypt.sign(json.dumps(block_content).encode())

    # add signature to block content
    block_content.update({"signature": bytes_to_string(signature)})

    log.important("Publishing release on update blockchain...")
    update_blockchain.add_block(
        json.dumps(block_content).encode(), topics=["update"]
    )
    update_blockchain.terminate()
    log.important(
        f"Done. Published release. Brenthy version {brenthy_version}, "
        f"Walytis_Beta version {walytis_beta_version}"
    )


def publish_project_on_ipfs() -> str:
    """Publish Brenthy's essential files to IPFS, returning their CID."""
    tempdir = tempfile.mkdtemp()

    shutil.copytree("../Brenthy", os.path.join(tempdir, "Brenthy"))
    shutil.copy("../__main__.py", os.path.join(tempdir, "__main__.py"))
    shutil.copy("../ReadMe.md", os.path.join(tempdir, "ReadMe.md"))

    if TESTING_BRENTHY:
        replace_brenthy_version_for_test_publish(
            os.path.join(
                tempdir, "Brenthy", "brenthy_tools_beta", "versions.py"
            )
        )

    if TESTING_WALYTIS_BETA:
        replace_walytis_beta_version_for_test_publish(
            os.path.join(
                tempdir,
                "Brenthy",
                "blockchains",
                "Walytis_Beta",
                "walytis_beta_tools",
                "versions.py",
            )
        )

    if os.path.exists(os.path.join(tempdir, "Brenthy", ".log")):
        os.remove(os.path.join(tempdir, "Brenthy", ".log"))
    if os.path.exists(os.path.join(tempdir, "Brenthy", ".log_archive")):
        shutil.rmtree(os.path.join(tempdir, "Brenthy", ".log_archive"))

    ipfs_cid = ipfs.files.publish(tempdir)

    shutil.rmtree(tempdir)

    return ipfs_cid


def replace_brenthy_version_for_test_publish(filepath: str) -> None:
    """Replace the version string in the specified versions.py file."""
    with open(filepath, "r") as file:
        project_data = file.read()

    project_data = project_data.replace(
        "BRENTHY_API_PROTOCOL_VERSION = ",
        "BRENTHY_API_PROTOCOL_VERSION = 9999",
    )
    with open(filepath, "w") as file:
        file.write(project_data)


def replace_walytis_beta_version_for_test_publish(filepath: str) -> None:
    """Replace real version string in the specified versions.py file."""
    with open(filepath, "r") as file:
        project_data = file.read()

    project_data = project_data.replace(
        "WALYTIS_BETA_PROTOCOL_VERSION = ",
        "WALYTIS_BETA_PROTOCOL_VERSION = 9999",
    )

    with open(filepath, "w") as file:
        file.write(project_data)


if __name__ == "__main__":
    publish_release()
