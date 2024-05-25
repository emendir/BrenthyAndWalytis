"""Brenthy's project metadata, as relevant for publications."""

import os

from brenthy_tools_beta.version_utils import version_to_string
from brenthy_tools_beta.versions import BRENTHY_CORE_VERSION

# pylint: disable=unused-variable
# pylint: disable=line-too-long
# pylint: disable=invalid-name

project_name = "Brenthy"
version = version_to_string(BRENTHY_CORE_VERSION)
author = "emendir"
description = (
    "A framework for developing and running the next generation of blockchains"
)
long_description = ""
if os.path.exists("ReadMe.md"):
    with open("ReadMe.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
long_description_content_type = "text/markdown"
url = (
    "https://ipfs.io/ipns/"
    "k2k4r8nismm5mmgrox2fci816xvj4l4cudnuc55gkfoealjuiaexbsup/Sites/"
    "BrenthyAndWalytis_Beta/Documentation/Brenthy/Meaning/Introduction.md.html"
)
project_urls = {
    "Source Code on IPNS": url,
    "Github": "",
}
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]

python_requires = ">=3.6"

# load install_requires data from requirements.txt
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
install_requires = []
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as file:
        install_requires = [line.strip("\n") for line in file.readlines()]
