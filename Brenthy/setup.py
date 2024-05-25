"""The setuptools script for creating the `brenthy_tools_beta` library."""

import os
import sys

import setuptools

if True:  # pylint: disable=using-constant-test
    sys.path.append(os.path.dirname(__file__))
    from brenthy_tools_beta.__project__ import (
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
    packages=[
        "brenthy_tools_beta",
        "brenthy_tools_beta/brenthy_api_protocols",
    ],
    python_requires=python_requires,
    install_requires=install_requires,
)
