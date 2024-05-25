_how to install Brenthy_
_For details on how Brenthy's installation process works at the technical level, see [../Technical/Installation.md](../Technical/Installation.md)._
_To uninstall Brenthy, see [./Uninstall.md](./Uninstall.md)_

# Installing Brenthy

**List of Platforms Supported by Auto-Installation**  
- Linux with systemd

For other platforms, complete and reliable installation scripts have not yet been fully developed.  
To install Brenthy on other platforms, follow the [manual installation guide](./ManualInstallation.md).  
To develop automated installation scripts for other platforms, study manual installation guide and the [technical installation documentation](../Technical/Installation.md)

## Installing

### Prerequisites
- Make sure you have [Python 3](https://python.org) and Python's package manager pip installed.
	- On most Linux operating systems, python comes preinstalled. You can check this by reading the output of  running the following commands:
		```sh
		# Check for python 3, depending on OS
		python --version
		python3 --version

		# Check for pip, depending on OS
		pip --version
		pip3 --version
		```
- Install [Python's virtualenv package](https://virtualenv.pypa.io/en/latest/installation.html)
	- On Debian-based operating systems run:
	```sh
	sudo apt install python3-virtualenv
	```

### Install Brenthy
Download Brenthy's source code, go into its directory and run it with Python. Make sure you are running it from a user with superuser privileges or root.
```shell
# make temporary directory
mkdir /tmp/brenthy_installation
cd /tmp/brenthy_installation
# download Brenthy source code
ipfs get /ipns/k2k4r8nismm5mmgrox2fci816xvj4l4cudnuc55gkfoealjuiaexbsup/Sites/BrenthyAndWalytis/Brenthy.zip
unzip Brenthy.zip

# Run Brenthy, it will offer to install itself.
python3 .
```

When running on a supported platform, Brenthy will offer to install itself.
After typing 'y', you will need to enter your password (if you are not already root), and then Brenthy will install itself.

Brenthy will install itself without asking if the `--install` or `--install-dont-run` flags are passed, for example:
```sh
python3 . --install
```

If you want Brenthy to use a different location for storing its blockchains' data than the default, create your custom directory first, then pass it with the `--data-dir` parameter when running Brenthy with python, for example:
```sh
python3 . --install --data-dir /path/to/blockchains_storage
```
## Installation Notes:
#### Debian, Ubuntu and Other Systemd-Enabled Linux
On linux systems with systemd, the Brenthy installation creates systemd services for both Brenthy and Kubo (IPFS).

You can always use the following commands to stop, start and restart those services running in the background:

```shell
# Brenthy
sudo systemctl stop brenthy
sudo systemctl start brenthy
sudo systemctl restart brenthy

# Kubo (IPFS)
sudo systemctl stop ipfs
sudo systemctl start ipfs
sudo systemctl restart ipfs
```
If you restart IPFS, you will need too restart Brenthy afterwards for it to work properly.