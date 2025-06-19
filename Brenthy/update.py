"""The machinery for Brenthy to update itself."""

# pylint: disable=global-statement
import importlib
import json
import os
import shutil
import sys
import tempfile
from threading import Lock

import blockchain_manager
import brenthy_tools_beta.versions
import run
from walytis_beta_tools._experimental.config import ipfs
from walytis_beta_api import (
    Block,
    BlocksListener,
    join_blockchain_from_zip,
    list_blockchain_ids,
)
from brenthy_tools_beta import log
from brenthy_tools_beta.utils import string_to_bytes
from brenthy_tools_beta.version_utils import (
    is_version_greater,
    version_from_string,
    version_to_string,
)
from cryptem import verify_signature
from install import am_i_installed, WE_ARE_IN_DOCKER


def get_walytis_appdata_dir():
    walytis = blockchain_manager.blockchain_modules["Walytis_Beta"]
    return walytis.get_walytis_appdata_dir()


update_blockchain_blocks_listener = None  # pylint: disable=invalid-name

PUBLISHER_PUBLIC_KEY = "0459f93b7e8c77ec5daad9e2625ef5421028a8bcc3f158ce5e5085e1fde012e4a943a97446574d92f4330ce74c059dd4f66e78313021b8a3cdb0af141d58a70d0c"  # pylint: disable=line-too-long
PREFERRED_SIG_ALGORITHM = "EC-secp256k1.SHA256"

verified_updates_path = os.path.join(".updates", "verified")

TESTING = WE_ARE_IN_DOCKER


def check_on_updates() -> None:
    """Listen on BrenthyUpdates for updates."""
    if not am_i_installed():
        log.important("Not checking on updates because I'm not installed.")
        return
    log.important("Checking on updates...")

    # Starting update Blockchain:
    global update_blockchain_blocks_listener

    # find the BrenthyUpdates or BrenthyUpdatesTEST blockchain
    brenthy_updates_bc = [
        blockchain_id
        for blockchain_id in list_blockchain_ids()
        if blockchain_id in {"BrenthyUpdates", "BrenthyUpdatesTEST"}
    ]
    if TESTING:
        if brenthy_updates_bc == ["BrenthyUpdates"]:
            switch_to_test_blockchain()  # restart brenthy
            return
    if not brenthy_updates_bc:
        log.important("Joining BrenthyUpdates...")

        zip_path = os.path.join(
            os.path.dirname(__file__), "InstallScripts", "BrenthyUpdates.zip"
        )
        join_blockchain_from_zip("BrenthyUpdates", zip_path)
        # shutil.rmtree(tempdir)
        brenthy_updates_bc = [
            blockchain_id
            for blockchain_id in list_blockchain_ids()
            if blockchain_id in {"BrenthyUpdates", "BrenthyUpdatesTEST"}
        ]

        if TESTING:
            switch_to_test_blockchain()  # restarts Brenthy
            return
    if brenthy_updates_bc:
        log.info("Listening for Brenthy updates...")
        if TESTING:
            update_blockchain_blocks_listener = BlocksListener(
                "BrenthyUpdatesTEST", on_update_released, "update"
            )
            # update_blockchain_blocks_listener = Blockchain(
            #     "BrenthyUpdatesTEST", "Brenthy", on_update_released)
            log.info("Using BrenthyUpdatesTEST...")
        else:
            update_blockchain_blocks_listener = BlocksListener(
                "BrenthyUpdates", on_update_released, "update"
            )
            # update_blockchain_blocks_listener = Blockchain(
            #     "BrenthyUpdates", "Brenthy", on_update_released)
    else:
        log.warning(
            "NOT listening for updates because we don't have the update "
            "blockchain."
        )


def switch_to_test_blockchain() -> None:
    """Switch from the BrenthyUpdates blockchain to BrenthyUpdatesTEST.

    Renames the BrenthyUpdates blockchain to BrenthyUpdatesTEST
    and restarts Brenthy.
    """
    log.important("Renaming BrenthyUpdates to BrenthyUpdatesTEST")
    log.debug(get_walytis_appdata_dir())
    brenthy_updates_dir = os.path.join(
        get_walytis_appdata_dir(), "BrenthyUpdates"
    )
    brenthy_updates_test_dir = os.path.join(
        get_walytis_appdata_dir(), "BrenthyUpdatesTEST"
    )

    if not os.path.exists(brenthy_updates_dir):
        dirname = os.path.dirname(brenthy_updates_dir)
        dir_list = []
        if os.path.exists(dirname):
            dir_list = os.listdir(dirname)
        log.error(f"BrenthyUpdates appdata doesn't exist! {dir_list}")
        sys.exit()
    log.important("Restarting Brenthy to using BrenthyUpdatesTEST")
    run.stop_brenthy()
    os.rename(brenthy_updates_dir, brenthy_updates_test_dir)
    run.restart_brenthy()


update_lock = Lock()


def on_update_released(block: Block) -> None:
    """Process an update block, exception-handled."""
    try:
        with update_lock:
            process_update_block(block)
    except Exception as e:  # pylint: disable=broad-exception-caught
        log.error(str(e) + "\n" + str(block.content))


def process_update_block(block: Block) -> bool:
    """Process a block about a new release of Brenthy.

    - check if it is relevant
    -> download and verify release
    """
    log.info("Processing update block...")
    data = json.loads(block.content.decode())
    update_brenthy_version = data["brenthy_version"]
    ipfs_cid = data["ipfs_cid"]
    signature = string_to_bytes(data["signature"])
    signature_data = json.dumps(
        {
            "brenthy_version": update_brenthy_version,
            "blockchains": data["blockchains"],
            "ipfs_cid": ipfs_cid,
            "signature_algorithm": data["signature_algorithm"],
        }
    ).encode()

    # currently we only know one signature algorithm
    if data["signature_algorithm"] != PREFERRED_SIG_ALGORITHM:
        log.warning(
            "Update: received Brenthy update block with unknown "
            "signature algorithm"
        )
        return False
    if not verify_signature(signature_data, PUBLISHER_PUBLIC_KEY, signature):
        log.warning(
            "Update: autheniticity check: received Brenthy update block with "
            "invalid signature"
        )
        return False
    log.info(f"Update: Received update release block {update_brenthy_version}")

    importlib.reload(brenthy_tools_beta.versions)
    current_brenthy_version = brenthy_tools_beta.versions.BRENTHY_CORE_VERSION
    current_blockchains = [
        {"blockchain_type": module.blockchain_type, "version": module.version}
        for module in blockchain_manager.blockchain_modules.values()
    ]

    # Decide whether or not to install this udpate by checking whether or not
    # it has a newer brenthy version or a newer blockchain version
    lets_update = False  # whether or not we should update

    # check if Brenthy version is greater than our current version
    if is_version_greater(update_brenthy_version, current_brenthy_version):
        lets_update = True
        log.info(
            f"Update: new version of Brenthy available: "
            f"{update_brenthy_version}"
        )

    # check the update's blockchains for newer versions and new blockchains
    for update_blockchain in data["blockchains"]:
        blockchain_known = False
        for current_blockchain in current_blockchains:
            current_blockchain_type = current_blockchain["blockchain_type"]
            if current_blockchain_type == update_blockchain["blockchain_type"]:
                blockchain_known = True
                # if update's blockchain version is greater than ours
                if is_version_greater(
                    update_blockchain["version"], current_blockchain["version"]
                ):
                    log.info(
                        f"Update: new version of {current_blockchain_type} "
                        f"available: {update_blockchain['version']}"
                    )
                    lets_update = True
                break
        if not blockchain_known:  # if blockchain type is new
            log.info(
                "Update: new blockchain type available: "
                f"{update_blockchain['blockchain_type']}"
            )
            lets_update = True

    if not lets_update:
        log.info(
            f"Update: update has nothing new, ignoring release message. {data}"
        )
        return False
    log.debug(f"Downloading update... {ipfs_cid}")
    if not os.path.exists(verified_updates_path):
        os.makedirs(verified_updates_path)
    download_path = tempfile.mkdtemp(dir=".updates")
    ipfs.files.download(ipfs_cid, download_path)
    log.debug("Verifying download...")
    release_path = os.path.join(download_path, ipfs_cid)
    if not verify_downloaded_release(release_path, ipfs_cid):
        shutil.rmtree(download_path)

        return False
    
    log.debug("Moving update...")
    shutil.move(
        release_path,
        os.path.join(
            verified_updates_path, version_to_string(update_brenthy_version)
        ),
    )

    shutil.rmtree(download_path)
    log.info(f"Update: Downloaded udpate {update_brenthy_version}")

    # install update
    check_for_installable_update()
    return True


def verify_downloaded_release(release_path: str, cid: str) -> bool:
    """Check the integrity and authenticity of a downloaded Brenthy release."""
    log.debug(f"Verifying update at {release_path}")
    real_cid = ipfs.files.publish(release_path)
    if not real_cid == cid:
        log.warning("update integrity check failed.")
        return False
    return True


def check_for_installable_update() -> None:
    """Check if we have verified updates ready to install.

    If more than one release has been downloaded, it tries installing the
    newest release first.
    Releases are tested before installation. If testing fails, the release
    is deleted.
    If testing succeeds, the release is installed.
    """
    log.important("Checking for installable update...")
    if not os.path.exists(verified_updates_path):
        return
    updates = os.listdir(verified_updates_path)
    if not updates:
        log.info("No updates available.")
        return
    if len(updates) > 1:
        log.warning(f"Multiple updates are ready for installation: {updates}")
    update = None

    # while we have any updates available, get latest one and test it
    # until we have settled on a working udpate
    while len(updates) > 0:
        # getting latest update
        update = updates[0]
        for u in updates:
            if is_version_greater(
                version_from_string(u), version_from_string(update)
            ):
                update = u
        update_path = os.path.join(verified_updates_path, update)

        if test_update(update_path):  # if testing succeeds
            break  # exit loop cause we've found a working update

        # update test failed:
        # remove downloaded update, reiterate this while loop
        log.error(f"update test failed for {update_path}")
        # shutil.rmtree(update_path)
        updates.remove(update)
        update = None

    # exit if we didn't find a working update
    if not update:
        log.info("All available updates failed testing and were removed.")
        return
    try:
        install_update(update)
    except Exception as e:
        log.error(f"Installation of update failed:\n{e}")


def test_update(update_path: str) -> bool:
    """Test a release of Brenthy (TODO)."""
    # TODO:
    if not os.path.exists(os.path.join(update_path, "__main__.py")):
        log.error(f"update test failed for {update_path}")

        return False

    log.info("Download update test successfull")
    return True


def install_update(update: str) -> None:
    """Install an already verified and tested release of Brenthy.

    The release is expected to be a folder under .updates/verified/
    The current installation is moved to a folder called .src_backup
    and is then replaced with the newest release.
    Brenthy is then restarted.
    """
    if not am_i_installed():
        log.important("Not checking on updates because I'm not installed.")
        return
    log.important(f"Installing update {update}")

    # backup current installation
    os.chdir("..")
    if os.path.exists(".src_backup"):
        shutil.rmtree(".src_backup")

    log.debug("Backing up current installation...")
    shutil.move("Brenthy", ".src_backup")

    # shutil.move(os.path.join(update_path, "Brenthy"), "Brenthy")
    update_path = os.path.join(".src_backup", ".updates", "verified", update)
    log.debug("Replacing current installation with update...")
    shutil.move(os.path.join(update_path, "Brenthy"), "Brenthy")

    log.debug("Restoring log files...")
    if os.path.exists(os.path.join(".src_backup", "brenthy.log")):
        shutil.copy(os.path.join(".src_backup", "brenthy.log"), "Brenthy")
    elif os.path.exists(os.path.join(".src_backup", ".log")):
        shutil.copy(
            os.path.join(".src_backup", ".log"),
            os.path.join("Brenthy", "brenthy.log"),
        )
    shutil.rmtree(update_path)
    log.important(f"Installed update {update}")


def terminate_updater() -> None:  # pylint: disable=unused-variable
    """Shut down the update system, clenaing up its resources."""
    if update_blockchain_blocks_listener:
        update_blockchain_blocks_listener.terminate()


if __name__ == "__main__":
    check_on_updates()
