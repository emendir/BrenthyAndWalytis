"""`brenthy_tools_beta`'s project metadata, as relevant for publications."""

# pylint: disable=unused-variable
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import os

print(__package__)
if __package__:
    from .version_utils import version_to_string
    from .versions import BRENTHY_TOOLS_VERSION
else:
    from version_utils import version_to_string  # pylint: disable=import-error
    from versions import BRENTHY_TOOLS_VERSION  # pylint: disable=import-error

project_name = os.path.basename(os.path.dirname(__file__))

version = version_to_string(BRENTHY_TOOLS_VERSION)

author = "emendir"
description = (
    "A library for interacting with Brenthy (`brenthy_api`) and a collection "
    "of tools common to Brenthy Core and `brenthy_api`."
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
    # "Documentation/Brenthy/Meaning/Introduction.md.html"
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
