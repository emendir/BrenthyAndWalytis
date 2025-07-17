#!/bin/bash

# the absolute path of this script's directory
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPT_DIR

set -e # Exit if any command fails

if ! [ -e ./Walytis_Beta/__init__.py ];then
  git clone --branch v2.4.19 --single-branch https://github.com/emendir/Walytis_Beta ./Walytis_Beta
fi
