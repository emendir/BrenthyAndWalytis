#!/bin/bash

set -e # exit on error

# the directory of this script
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# the root directory of this project
PROJ_DIR=$(realpath $SCRIPT_DIR/../..)
cd $PROJ_DIR


# delete pip caches to ensure the libraries will be rebuilt
rm -r Brenthy/brenthy_tools_beta.egg-info >/dev/null 2>/dev/null || true
rm -r Brenthy/build >/dev/null 2>/dev/null || true
rm -r Brenthy/blockchains/Walytis_Beta/walytis_beta_api.egg-info >/dev/null 2>/dev/null || true
rm -r Brenthy/blockchains/Walytis_Beta/build >/dev/null 2>/dev/null || true

docker build -t local/brenthy_testing -f tests/brenthy_docker/brenthy_testing.dockerfile .

## Run with:
# docker run -it --privileged local/brenthy_testing