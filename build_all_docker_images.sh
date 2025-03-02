#!/bin/bash

# the absolute path of this script's directory
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPT_DIR

set -e # Exit if any command fails

tests/brenthy_docker/build_brenthy_prereqs.sh
tests/brenthy_docker/build_brenthy_testing.sh
Brenthy/Docker/build_brenthy_docker.sh
Brenthy/Docker/build_ipfs_docker.sh
