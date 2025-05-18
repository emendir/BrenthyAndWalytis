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

- `walytis_beta_api` depends on the `brenthy_tools_beta` library. See [Installing-brenthy_tools](https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Brenthy/User/Installing-brenthy_tools.md).

### Installation

The `walytis_beta_api` is built using the [`legacy_packaging/walytis_beta_api/pyproject.toml`](/legacy_packaging/walytis_beta_api/pyproject.toml) file.
Follow these steps to install it using pip:

1. Navigate to the `legacy_packaging/walytis_beta_api` directory inside of this repository.

```sh
cd legacy_packaging/walytis_beta_api
```

2. Build and install the package using pip:

```sh
pip install .
```
