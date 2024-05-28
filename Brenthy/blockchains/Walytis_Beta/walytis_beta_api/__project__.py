"""`walytis_beta_api`'s project metadata, as relevant for publications."""

import os

from brenthy_tools_beta.version_utils import version_to_string

if __package__:
    print(__package__)
    from .versions import WALYTIS_BETA_API_VERSION
else:
    # pylint: disable=import-error
    from versions import WALYTIS_BETA_API_VERSION

project_name = os.path.basename(os.path.dirname(__file__))
version = version_to_string(WALYTIS_BETA_API_VERSION)
author = "emendir"
description = (
    "A library for interacting with Walytis_Beta: "
    "a lightweight, flexible, non-linear blockchain."
)
long_description = ""
if os.path.exists("ReadMe.md"):
    with open("ReadMe.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
long_description_content_type = "text/markdown"
url = (
    "https://ipfs.io/ipns/"
    "k2k4r8nismm5mmgrox2fci816xvj4l4cudnuc55gkfoealjuiaexbsup"
    "/Sites/BrenthyAndWalytis/"
    # "Documentation/Walytis/Meaning/Introduction.md.html"
)
project_urls = {
    "IPNS": url,
    "Github": "https://github.com/emendir/BrenthyAndWalytis",
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
    with open(requirements_path, "r") as file:
        install_requires = [line.strip("\n") for line in file.readlines()]
