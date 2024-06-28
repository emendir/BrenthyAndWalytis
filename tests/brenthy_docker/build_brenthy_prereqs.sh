#!/bin/bash
# Get the directory of this script
work_dir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# change to root directory of the Brenthy repo
cd $work_dir/../..

# delete pip caches to ensure the libraries will be rebuilt
rm -r Brenthy/brenthy_tools_beta.egg-info >/dev/null 2>/dev/null
rm -r Brenthy/build >/dev/null 2>/dev/null
rm -r Brenthy/blockchains/Walytis_Beta/walytis_beta_api.egg-info >/dev/null 2>/dev/null
rm -r Brenthy/blockchains/Walytis_Beta/build >/dev/null 2>/dev/null

docker build -t local/brenthy_prereqs -f tests/brenthy_docker/brenthy_prereqs.dockerfile .

## Run with:
# docker run -it --privileged local/brenthy_prereqs