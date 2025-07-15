#!/bin/bash

set -e # exit on error

# the directory of this script
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# the root directory of this project
PROJ_DIR=$(realpath $SCRIPT_DIR/../..)
cd $PROJ_DIR

# copy all paths listed in ./python_packages.txt to ./python_packages/
# paths are relative to $PROJ_DIR
PYTHON_PACKAGES_DIR="$SCRIPT_DIR/python_packages/"
PACKAGES_LIST="$SCRIPT_DIR/python_packages.txt"
if ! [ -e $PYTHON_PACKAGES_DIR ];then
    mkdir -p $PYTHON_PACKAGES_DIR
fi
if [[ -f "$PACKAGES_LIST" ]]; then
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^# ]] && continue

        rsync -XAvaL "$line" "$PYTHON_PACKAGES_DIR"
    done < "$PACKAGES_LIST"
fi

# delete pip caches to ensure the libraries will be rebuilt
rm -r Brenthy/brenthy_tools_beta.egg-info >/dev/null 2>/dev/null || true
rm -r Brenthy/build >/dev/null 2>/dev/null || true
rm -r Brenthy/blockchains/Walytis_Beta/walytis_beta_api.egg-info >/dev/null 2>/dev/null || true
rm -r Brenthy/blockchains/Walytis_Beta/build >/dev/null 2>/dev/null || true

docker build -t local/brenthy_prereqs -f tests/brenthy_docker/brenthy_prereqs.dockerfile .

## Run with:
# docker run -it --privileged local/brenthy_prereqs