_how to install `walytis_api`_

`walytis_api` is the python library which applications can use to communicate with the locally running Walytis Core software to interact with blockchains.
During the time of the beta release of Walytis, we will use `walytis_beta_api`.
When `walytis_api` is released in the future, it will just be an update of `walytis_beta_api`, possible with a few breaking changes.

# Installation
## Option 1: Install from PyPI
The simplest way to install `walytis_beta_api`is with pip from the Python Package Index:
```sh
pip install walytis_beta_api
```
## Option 2: Install from Source
### Prerequisites

- `walytis_beta_api` depends on the `brenthy_tools_beta` library. See [Installing-brenthy_tools](/Documentation/Brenthy/User/Installing-brenthy_tools.md).
### Installation

The `walytis_beta_api` is built using the [`Brenthy/blockchains/Walytis_Beta/setup.py`](/Brenthy/blockchains/Walytis_Beta/setup.py)  file.
Follow these steps to install it using pip:
1. Navigate to the `Brenthy/blockchains/Walytis_Beta` directory inside of this repository.
```sh
cd Brenthy/blockchains/Walytis_Beta
```
2. Build and install the package using pip:
```sh
pip install .
```