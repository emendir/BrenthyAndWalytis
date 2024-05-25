"""Defines the paths of various appdata locations."""

# pylint: disable=unused-variable

import os.path

from install import am_i_installed

install_dir: str
appdata_dir: str
logs_dir: str

if am_i_installed():
    # set the appdata directory to the Brenthy installation directory
    install_dir = os.path.dirname(os.path.dirname(__file__))
    appdata_dir = install_dir
    logs_dir = install_dir
else:  # Brenthy is not installed
    # only import appdirs here, so that it doesn't raise an error
    # in a Brenthy installation where this library failed to install
    import appdirs

    # use the user appdata path specified by the OS
    appdata_dir = os.path.join(appdirs.user_data_dir(), "Brenthy")
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)
    logs_dir = appdata_dir

blockchaintypes_dir = os.path.join(appdata_dir, "BlockchainData")
