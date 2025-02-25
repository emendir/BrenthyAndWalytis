#!/bin/bash
# Get the directory of this script
work_dir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# change to root directory of the Brenthy repo
cd $work_dir

docker build -t local/ipfs -f ipfs.dockerfile .

## Run with:
# docker run -it --privileged local/brenthy