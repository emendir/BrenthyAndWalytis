"""Setuptools script for walytis_beta_api."""

import os
import sys

import setuptools

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if True:
    # load walytis_beta_api.__project__
    # NOT TO BE CONFUSED with Walytis_Beta.__project__
    sys.path.insert(
        0, os.path.join(os.path.dirname(__file__), "walytis_beta_api")
    )
    from __project__ import (
        author,
        classifiers,
        description,
        install_requires,
        long_description,
        long_description_content_type,
        project_name,
        project_urls,
        python_requires,
        url,
        version,
    )
setuptools.setup(
    name=project_name,
    version=version,
    author=author,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url=url,
    project_urls=project_urls,
    classifiers=classifiers,
    packages=["walytis_beta_api"],
    python_requires=python_requires,
    install_requires=install_requires,
)
