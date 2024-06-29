#!/bin/python
"""Install all python packages in this repository."""

import importlib
import importlib.util
import os
import sys
from types import ModuleType


def load_module_from_path(path: str) -> ModuleType:
    """Load a python module given its path."""
    module_name = os.path.basename(path).strip(".py")
    if os.path.isdir(path):
        path = os.path.join(path, "__init__.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run() -> None:
    """Install all python packages in this repository."""
    project_dir = os.path.abspath(os.path.dirname(__file__))

    install_brenthy_docker = load_module_from_path(os.path.join(
        project_dir, "tests", "brenthy_docker", "pip_install.py"
    ))
    install_brenthy_tools_beta = load_module_from_path(os.path.join(
        project_dir, "Brenthy", "pip_install.py"
    ))
    install_walytis_beta_api = load_module_from_path(os.path.join(
        project_dir,  "Brenthy", "blockchains", "Walytis_Beta", "pip_install.py"
    ))

    install_brenthy_docker.run()
    install_brenthy_tools_beta.run()
    install_walytis_beta_api.run()


if __name__ == "__main__":
    run()
