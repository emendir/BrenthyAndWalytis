#!/usr/bin/python3
"""Install the package in this directory using pip.

This script forces rebuilding this package and installs it for the python
interpreter this script is executed with.
"""

import os
import shutil

import pip
import toml


def run() -> None:
    """Reinstall the python package located in this directory using pip."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    package_data = toml.load(os.path.join(project_dir, "pyproject.toml"))
    package_name = package_data["project"]["name"]

    # list of directories that need to be deleted before running pip install
    dirs_to_delete = [f"{package_name}.egg-info", "build"]

    # delete all necessary directories
    for directory in dirs_to_delete:
        abs_dir = os.path.join(project_dir, directory)
        if os.path.isdir(abs_dir):
            shutil.rmtree(abs_dir)

    # run pip install for this package
    pip.main(["install", "--break-system-packages", project_dir])


if __name__ == "__main__":
    run()
