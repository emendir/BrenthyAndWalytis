"""The machinery that interacts with this program's appdata."""

# pylint: disable=import-error

import json
import os.path
import shutil
import tempfile
from abc import ABC
from threading import Event, Lock

from brenthy_tools_beta import log
import os

walytis_beta_appdata_dir = ""


def set_appdata_dir(appdata_dir: str):
    global walytis_beta_appdata_dir
    log.info(f"Walytis: Setting appdata: {walytis_beta_appdata_dir}")
    walytis_beta_appdata_dir = appdata_dir
    if not os.path.exists(walytis_beta_appdata_dir):
        os.makedirs(walytis_beta_appdata_dir)
    if not os.path.exists(_get_temp_root_dir()):
        os.makedirs(_get_temp_root_dir())


def get_walytis_appdata_dir():
    return walytis_beta_appdata_dir


def _get_temp_root_dir():
    return os.path.join(walytis_beta_appdata_dir, ".tmp")


def create_temp_dir():
    return tempfile.mkdtemp(dir=_get_temp_root_dir())


class BlockchainAppdata(ABC):
    """Blockchain class's appdata machinery, inherited by class Blockchain."""

    id = ""
    name = ""
    appdata_dir = ""  # defined in Walytis_Beta
    invitations_path = ""
    config_path = ""

    def __init__(self):
        """Load this blockchain's attributes from appdata."""
        self.config_lock = (
            Lock()
        )  # lock for accessing invitations file and config file
        self.appdata_initialised = Event()

        # directories
        if not os.path.exists(self.appdata_dir):
            raise FileNotFoundError(
                "Blockchain Appdata doesn't exist! "
                f"{self.name} {self.appdata_dir}"
            )
        self.received_blocks_dir = os.path.join(
            self.appdata_dir, "ReceivedBlocks"
        )
        if not os.path.exists(self.received_blocks_dir):
            os.mkdir(self.received_blocks_dir)
        self.known_blocks_index_dir = os.path.join(
            self.appdata_dir, "KnownBlocksIndex"
        )
        if not os.path.exists(self.known_blocks_index_dir):
            os.mkdir(self.known_blocks_index_dir)
        self.invitations_path = os.path.join(
            self.appdata_dir, "Invitations.json"
        )
        self.config_path = os.path.join(self.appdata_dir, "Config.json")
        self.load_invitations()
        self.load_config()
        self.ipfs_peers_path = os.path.join(
            self.appdata_dir, "IPFS-Peers.json"
        )
        self.appdata_initialised.set()

    def zip_appdata(self) -> str:
        """Create a zip file of all this blockchain's data."""
        # Temporarily replace appdata file with list of invitations
        # with a list of shared invitations only
        self.config_lock.acquire()

        shared_invitations = [
            invitation
            for invitation in self.invitations
            if json.loads(invitation)["shared"]
        ]
        temppath = os.path.join(
            os.path.dirname(self.appdata_dir),
            f"{self.blockchain_id}Invitations.json",
        )
        if os.path.exists(self.invitations_path):
            shutil.move(self.invitations_path, temppath)
        with open(self.invitations_path, "w+") as f:
            f.writelines(json.dumps(shared_invitations))

        shutil.make_archive(self.appdata_dir, "zip", self.appdata_dir)

        # restore full appdata invitations file
        os.remove(self.invitations_path)
        if os.path.exists(temppath):
            shutil.move(temppath, self.invitations_path)
        self.config_lock.release()

        zip_path = self.appdata_dir + ".zip"

        tempdir = tempfile.mkdtemp()
        temp_zip_path = os.path.join(tempdir, os.path.basename(zip_path))
        shutil.move(zip_path, temp_zip_path)
        return temp_zip_path

    def load_invitations(self) -> None:
        """Load invitations from appdata."""
        self.config_lock.acquire()
        if os.path.exists(self.invitations_path):
            with open(self.invitations_path, "r") as reader:
                self.invitations = json.loads(reader.read())
        self.config_lock.release()

    def save_invitations(self) -> None:
        """Save invitations to appdata."""
        self.config_lock.acquire()
        with open(self.invitations_path, "w+") as writer:
            writer.write(json.dumps(self.invitations))
        self.config_lock.release()

    def load_config(self) -> None:
        """Load user-defined configurations from appdata.

        Only fills the Walytis_Beta class's attributes if they are empty,
        doesn't override them. If those attributes already have non-empty,
        their values are saved to the config file.
        """
        self.config_lock.acquire()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as reader:
                    data = json.loads(reader.read())
                if not self.name and "name" in data.keys():
                    self.name = data["name"]
            except Exception as error:
                error_message = (
                    "Walytis_BetaAppdata: failed to parse config.json: "
                    + str(error)
                )
                log.error(error_message)
        self.save_config(already_locked=True)
        self.config_lock.release()

    def save_config(self, already_locked: bool = False) -> None:
        """Save user-defined configurations for this blockchain."""
        if not already_locked:
            self.config_lock.acquire()
        data = {"name": self.name}
        with open(self.config_path, "w+") as writer:
            writer.write(json.dumps(data))
        if not already_locked:
            self.config_lock.release()
