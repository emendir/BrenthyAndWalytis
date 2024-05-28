_how to run Brenthy from the project's source code, without installing it_

# Running Brenthy From Source:
## Prerequisite Knowledge and Understanding
- basic knowledge of working with the Python programming language and its package manager pip (or an alternative) on your operating system
- basic knowledge and understanding of what [IPFS, the InterPlanetary FileSystem](https://ipfs.io), is and how to use it on your operating system
- ability to use a command line interface to your operating system (called 'terminal' on Linux & Mac, command prompt on Windows)

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
- the python libraries listed in `Brenthy/requirements.txt`

## Running from Shell
1. Navigate to the `Brenthy` directory inside of this repository.
```sh
cd Brenthy
```
2. Make sure you are in the correct directory. It is not the root folder of this project's repository, but a subfolder of it called `Brenthy`. The contents of the folder should look something like this:
	```
	Brenthy
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
	├── requirements.txt
	├── run.py
	├── setup.py
	├── uninstall.py
	└── update.py
	```
3. Run the folder in python:
	```sh
	python .
	```
	Optionally, you can pass command-line arguments, for example:
	```sh
	python . --dont-install
	```
	
### Command-Line Arguments:
- `--dont-install` don't offer to install Brenthy, just run from source
- `--install` don't ask user about installation, just install it and run the installation
- `--install-dont-run` same as `--install`, but don't run the installed Brenthy when finished
- `--dont-update` don't check for or install updates
- `--print-log-level [ARG]` set which log level and above should be printed to console. Options are: `info`, `important`, `warning`, `error`

## Running From Within Python
1. import the `Brenthy/run.py` module:
```python
# tell python the folder where it will find the run.py file,
# skip this if you're running python from within that folder
import sys
sys.path.append("/path/to/BrenthyAndWalytisProject/Brenthy/")

# import the run module under the clearer alias of 'brenthy'
import run as brenthy
```
2. Optionally configure some settings:
```python
brenthy.TRY_INSTALL = False
brenthy.CHECK_UPDATES = False
```
3. call the `run_brenthy` function:
```python
brenthy.run_brenthy()
```
Apart from `run_brenthy()`, you also have access to the `stop_brenthy()` and `restart_brenthy()` functions.
