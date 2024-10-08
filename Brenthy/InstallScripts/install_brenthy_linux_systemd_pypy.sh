#!/bin/bash
# must be run with root privileges from the directory of Brenthy's source

# get arguments passed to script:
install_dir=$1
data_dir=$2
run_brenthy=$3 # True of False; whether or not the installed Brenthy should be run when finished

echo "Running Brenthy Installer for Linux with Systemd using PyPy with args:"
echo "Install Dir: $install_dir"
echo "Data Dir:    $data_dir"
echo "Run Brenthy: $run_brenthy"

# Check prerequisites:
PREREQUISITES=("wget")
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


# Get the CPU architecture using uname
ARCH=$(uname -m)

# Check the architecture and set the variable accordingly
if [ "$ARCH" == "x86_64" ]; then
    PYPY_URL=https://downloads.python.org/pypy/pypy3.10-v7.3.17-linux64.tar.bz2
elif [ "$ARCH" == "aarch64" ]; then
    PYPY_URL=https://downloads.python.org/pypy/pypy3.10-v7.3.17-aarch64.tar.bz2
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

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
rm ./Brenthy/*.log >/dev/null 2>/dev/null
rm -r ./Brenthy/.log_archive >/dev/null 2>/dev/null
rm -r ./Brenthy/.brenthy_api_log_archive >/dev/null 2>/dev/null


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



if [ -e $install_dir/we_are_in_docker ] && [ -d $install_dir/Python ];then
  echo "Skipping Python installation."
else
  # create python virtual environment in install_dir and install all needed libraries there
  echo "Installing Brenthy's python environment using PyPy..."
  cd $install_dir ||exit 1

  # create Python dir
  if [ -d $install_dir/Python ];then
    rm -r $install_dir/Python
  fi
  mkdir $install_dir/Python

  # download pypy to a temporary directory
  TEMP_DIR=$(mktemp -d)
  wget -P $TEMP_DIR $PYPY_URL
  ARCHIVE_FILENAME=$(basename $PYPY_URL)
  tar -xjf $TEMP_DIR/$ARCHIVE_FILENAME -C $TEMP_DIR
  EXTRACTED_DIR_NAME="${ARCHIVE_FILENAME%.tar.bz2}"

  mv ${TEMP_DIR}/${EXTRACTED_DIR_NAME}/* $install_dir/Python/

  # install pip, the package manager
  Python/bin/python -m ensurepip
  Python/bin/python -m pip -qq install --upgrade pip

  # install a specific version of ecies, as the default's doesn't currently work
  Python/bin/python -m pip -qq install eciespy@git+https://github.com/ecies/py
  if ! [ "$?" = "0" ];then exit 1;fi
  Python/bin/python -m pip -qq install -r $install_dir/Brenthy/requirements.txt
  if ! [ "$?" = "0" ];then exit 1;fi
fi
# register Brenthy as a service/background process, and running it
echo "Registering systemd service..."
echo "[Unit]
Description=the platform for developing and running the next generation of blockchains
Wants=ipfs.service

[Service]
User=brenthy
WorkingDirectory=${install_dir}/Brenthy
ExecStart=${install_dir}/Python/bin/python ${install_dir}/Brenthy

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/brenthy.service


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

