#!/bin/bash
# must be run with root privileges from the directory of Brenthy's source

# get arguments passed to script:
install_dir=$1
data_dir=$2
run_brenthy=$3 # True of False; whether or not the installed Brenthy should be run when finished
docker_testing=$4 # True of False; whether or not this script is being run for docker testing image

set -e # Exit if any command fails

# the absolute path of this script's directory
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJ_DIR=$(realpath $SCRIPT_DIR/../)
cd $PROJ_DIR

echo "Running Brenthy Installer for Linux with Systemd using CPython with args:"
echo "Install Dir: $install_dir"
echo "Data Dir:    $data_dir"
echo "Run Brenthy: $run_brenthy"

# Check prerequisites:
PREREQUISITES=("virtualenv")
DEF_DATA_DIR=$install_dir/BlockchainData

# Iterate over the install methods
for prerequisite in "${PREREQUISITES[@]}"; do
  # Check if the command is available
  if ! command -v $prerequisite &> /dev/null; then
    echo -e "$prerequisite is not available, please install it first"
    exit 1
  fi
done



echo "Current working directory: $(pwd)"


# create install_dir
if [ -d $install_dir/Brenthy ];then
  rm -r $install_dir/Brenthy
fi
mkdir -p $install_dir/Brenthy

# create data_dir as a directory or symlink to the user-provided directory
if [[ "$data_dir" == "$DEF_DATA_DIR" ]];then
  if [ ! -d $data_dir ];then
    mkdir $data_dir
  fi
else
  if [ ! -e $data_dir ];then
    echo "The provided data directory doesn't exist: $data_dir"
    exit 1
  fi
  if [ ! -d $data_dir ];then
    echo "The provided data directory isn't a directory: $data_dir"
    exit 1
  fi
  
  if [ -d "$DEF_DATA_DIR" ] && [ "$(ls -A "$DEF_DATA_DIR")" ];then
    echo "$DEF_DATA_DIR already exists! Please backup and remove it."
    exit 1
  fi
  ln -s $data_dir $DEF_DATA_DIR
fi


# copy Brenthy source code to install_dir
echo "Copying files to installation directory..."
cp -r . $install_dir/Brenthy
rm ./Brenthy/*.log >/dev/null 2>/dev/null || true
rm -r ./Brenthy/.log_archive >/dev/null 2>/dev/null || true
rm -r ./Brenthy/.brenthy_api_log_archive >/dev/null 2>/dev/null || true
if [[ "$docker_testing" == "true" || "$docker_testing" == "True" ]];then
  echo "Skipping Walytis download..."
else
  $install_dir/Brenthy/blockchains/install_walytis_beta.sh
fi

echo "Creating OS user..."
# add brenthy user
adduser --system --home $install_dir brenthy -q

echo "Setting file permissions..."
# Make brenthy the owner of the installation and data directories
chown -R brenthy:nogroup ${install_dir}
chown -R brenthy:nogroup ${data_dir}

# allow user to read, write, open directories, and execute files if any user may already execute the file
# allow group to read, open directories , and execute files if any user may already execute the file
chmod u=rwX,go=rX ${install_dir}
chmod u=rwX,go=rX ${data_dir}

# remove execute permission from all files for group and other recursively
find ${install_dir} -type f -exec chmod go-x {} +
find ${data_dir} -type f -exec chmod go-x {} +


if [ -e /.dockerenv ] &&  [ -d $install_dir/Python ];then
  echo "Skipping Python installation."
else
  # create python virtual environment in install_dir and install all needed libraries there
  echo "Installing Brenthy's python environment..."
  # cd $install_dir ||exit 1
  if [ -d $install_dir/Python ];then
    rm -r $install_dir/Python
  fi
  virtualenv $install_dir/Python
  source $install_dir/Python/bin/activate
  pip install -q --root-user-action ignore -r $install_dir/Brenthy/requirements.txt
  # install brenthy_tools_beta from source
  pip install -q --root-user-action ignore -e $install_dir/Brenthy/

  pip install -q --root-user-action ignore -r $install_dir/Brenthy/blockchains/Walytis_Beta/requirements.txt
  pip install -q --root-user-action ignore -e $install_dir/Brenthy/blockchains/Walytis_Beta/legacy_packaging/walytis_beta_api
  
  # # rm -r $install_dir/Brenthy/build/
  # # install walytis_beta library from source
  # Python/bin/python -m pip -qq install --root-user-action ignore -e $install_dir/Brenthy/blockchains/Walytis_Beta/
  # # rm -r $install_dir/Brenthy/blockchains/Walytis_Beta/build/
  # rm -r $install_dir/Brenthy/blockchains/Walytis_Beta/src/*.egg-info
fi

# register Brenthy as a service/background process, and running it
echo "Registering systemd service..."
echo "[Unit]
Description=the platform for developing and deploying the next generation of blockchains
Wants=ipfs.service

[Service]
User=brenthy
WorkingDirectory=${install_dir}/Brenthy
ExecStart=${install_dir}/Python/bin/python ${install_dir}/Brenthy --dont-install
Restart=always

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/brenthy.service

if [[ "$docker_testing" == "true" || "$docker_testing" == "True" ]];then
  # manually enable systemd service
  if ! [ -e /etc/systemd/system/brenthy.service ];then
    ln -s /etc/systemd/system/brenthy.service /etc/systemd/system/multi-user.target.wants/brenthy.service
  fi
  exit 0;
fi

systemctl daemon-reload
systemctl enable brenthy

if [[ "$run_brenthy" == "true" || "$run_brenthy" == "True" ]];then
  echo "Loading brenthy service..."
  systemctl restart brenthy # start brenthy service, restart if old version is still running

  # Check if brenthy is running
  sleep 1
  if systemctl is-active --quiet brenthy; then
    echo "Installation succeeded!"
  else
    echo "Installation failed."
    exit 1
  fi
fi

