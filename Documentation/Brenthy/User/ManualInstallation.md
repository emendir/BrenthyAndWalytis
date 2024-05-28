_how to install Brenthy and each of its components manually_
_This is useful for installing Brenthy on operating systems for which no fully automated Brenthy installer has been built yet._
_To install Brenthy using an automated installer, see [InstallingBrenthy](InstallingBrenthy.md)_
_For detailed documentation on how the automated installation works, see [../Technical/Installation.md](../Technical/Installation.md)_
_This guide is written generically to apply to all operating systems. It therefore does not provide detailed step-by-step instructions, instead it provides generic instructions which the reader must apply to their operating system. Examples for more detailed steps are sometimes provided for Debian-based Linux OSs._

# Installing Brenthy Manually

## User's Prerequisite Knowledge & Skill
- working in the command-line interface
- basics of how the Brenthy installation works and the purpose of all its different aspects (see the the [Installation Form](../Technical/Installation.md#installation-form) and [Purpose of Installation](../Technical/Installation.md#purpose-of-installation) sections of [../Technical/Installation.md](../Technical/Installation.md))
## Prerequisites
- [Python3](https://www.python.org/) and Python's package manager pip
	- On most Linux operating systems, python comes preinstalled. You can check this by reading the output of  running the following commands:
		```sh
		# Check for python 3, depending on OS
		python --version
		python3 --version

		# Check for pip, depending on OS
		pip --version
		pip3 --version
		```
- [Python's virtualenv package](https://virtualenv.pypa.io/en/latest/installation.html)
	- On Debian-based operating systems, run:
	```sh
	sudo apt install python3-virtualenv
	```
- IPFS
	- Make sure you have installed and initialised [IPFS](https://docs.ipfs.tech/install/command-line/)
	- Enable IPFS' experimental LibP2P-Stream-Mounting feature by running the following command:
	```sh
	ipfs config --json Experimental.Libp2pStreamMounting true
	```
	- Run IPFS with the following command:
	```sh
	ipfs daemon --enable-pubsub-experiment
	```

## Brenthy Installation
_Once you've installed the systems listed in [Prerequisites](./ManualInstallation.md#prerequisites), you are ready to install Brenthy itself. Follow these steps to do so:_
1. Choose an installation directory. This is the folder where Brenthy's source code, update backups and log files will be stored. We will refer to it as `INSTALL_DIR` in the rest of this guide.
2. Choose and create a storage directory. This is the folder where blockchains will store their blocks and other data. We will refer to it as `DATA_DIR` in the rest of this guide. The default  `DATA_DIR` is  a subfolder of the `INSTALL_DIR` called `BlockchainData`. If you are using a different path, create a symlink from the default data directory to your custom `DATA_DIR`:
```sh
ln -s $DATA_DIR $INSTALL_DIR/BlockchainData
```
3. Move the Brenthy source code folder (the `Brenthy` subfolder of this project's root) to `INSTALL_DIR`. The directory tree should look something like this:
```
INSTALL_DIR
└── Brenthy
	├── api_terminal
	├── app_data.py
	├── blockchain_manager.py
	├── blockchains
	├── brenthy_tools_beta
	├── install.py
	├── InstallScripts
	├── __main__.py
	├── pip_install.py
	├── __project__.py
	├── ReadMe.md
	├── recent_blocks_record.py
	├── requirements.txt
	├── run.py
	├── setup.py
	├── uninstall.py
	└── update.py
```
1. In `INSTALL_DIR`, create a python virtual environment. In it, install all the python libraries listed in `Brenthy/requirements.txt`
	```sh
	# Linux
	cd $INSTALL_DIR
	
	# create virtual environment
	virtualenv venv
	
	# in the virtual environment, install the necessary libraries
	source venv/bin/activate
	pip install -r Brenthy/requirements.txt
	```
5. On you operating system, create a system user called `brenthy` with no login permissions and a home directory at `INSTALL_DIR`. This user will own your `INSTALL_DIR` and `DATA_DIR` folders and will run Brenthy.
	```sh
	# Linux
	useradd --system --home $INSTALL_DIR -M -r -s /usr/sbin/nologin brenthy
	```
6. Change the ownership of the `INSTALL_DIR` and `DATA_DIR` folders and their content to the `brenthy` user.
	```sh
	# Linux
	chown -R brenthy $INSTALL_DIR
	chown -R brenthy $DATA_DIR
	```
7. Change the permissions of the `INSTALL_DIR` and `DATA_DIR` folders and their content to read-only for everybody other than the `brenthy` user.
8. Configure your operating system to run the installation directory using the virtual python environment as the `brenthy` user automatically on startup. On Linux, the command to run the source code using the virtual environment is:
	```sh
	$INSTALL_DIR/venv/bin/python $INSTALL_DIR/Brenthy
	```
	