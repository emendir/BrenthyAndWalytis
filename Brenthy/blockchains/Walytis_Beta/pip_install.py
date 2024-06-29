#!/usr/bin/python3
"""Rebuild and install this package.

Forces rebuilding by deleting caches,
and installs for the python interpreter this script is executed with.
"""

import os
import shutil

import pip


def run():
    # list of directories that need to be deleted before running pip install
    dirs_to_delete = ["walytis_beta_api.egg-info", "build"]

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # delete all necessary directories
    for dir in dirs_to_delete:
        abs_dir = os.path.join(current_dir, dir)
        if os.path.isdir(abs_dir):
            shutil.rmtree(abs_dir)

    # run pip install for this package
    pip.main(["install", "--break-system-packages", current_dir])


if __name__ == "__main__":
    run()
