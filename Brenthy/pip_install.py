#!/usr/bin/python3
"""Install `brenthy_tools_beta` using pip.

This script forces rebuilding this package and installs it for the python
interpreter this script is executed with.
"""

import os
import shutil

import pip

# list of directories that need to be deleted before running pip install
dirs_to_delete = ["brenthy_tools_beta.egg-info", "build"]

current_dir = os.path.dirname(os.path.abspath(__file__))

# delete all necessary directories
for directory in dirs_to_delete:
    abs_dir = os.path.join(current_dir, directory)
    if os.path.isdir(abs_dir):
        shutil.rmtree(abs_dir)

# run pip install for this package
pip.main(["install", "--break-system-packages", current_dir])
