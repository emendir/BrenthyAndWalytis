\_How to install the `brenthy_tools` python library.

# Installing brenthy_tools

`brenthy_tools` is a python library.
Crucially, it contains the `brenthy_api` module which blockchain libraries such as `walytis_api` use to communicate with their actual blockchain software via Brenthy.

During the time of the beta release of Brenthy, we will use `brenthy_tools_beta`.
When `brenthy_tools` is released in the future, it will just be an update of `brenthy_tools_beta`, possible with a few breaking changes.

## Option 1: Install from PyPI

The simplest way to install `brenthy_tools_beta`is with pip from the Python Package Index:

```sh
pip install brenthy_tools_beta
```

## Option 2: Install from Source

The `brenthy_tools_beta` is built using the [`Brenthy/pyproject.toml`](/Brenthy/pyproject.toml) file.
Follow these steps to install it using pip:

1. Navigate to the `Brenthy` directory inside of this repository.

```sh
cd Brenthy
```

2. Make sure you are in the correct directory. It is not the root folder of this project's repository, but a subfolder of it called `Brenthy`. The contents of the folder should look something like this:
   ```
   Brenthy
   ├── api_terminal
   ├── app_data.py
   ├── blockchain_manager.py
   ├── blockchains
   ├── brenthy_tools_beta
   ├── install.py
   ├── InstallScripts
   ├── __main__.py
   ├── pip_install.py
   ├── __project__.py
   ├── ReadMe.md
   ├── requirements.txt
   ├── run.py
   ├── pyproject.toml
   ├── uninstall.py
   └── update.py
   ```
   Crucially, this folder contains the `pyproject.toml` script used for building the package.
3. Build and install the package using pip:

```sh
pip install .
```
