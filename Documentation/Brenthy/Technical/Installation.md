_how Brenthy's installation process works_
_For user instructions on how to install Brenthy using an automated installer, see [../User/Installation.md](/Documentation/Brenthy/User/InstallingBrenthy.md)._
_For instructions on how to install Brenthy and its components manually, see [../User/ManualInstallation.md](../User/ManualInstallation.md)_

# Brenthy Installation

## Installation Form
Even when installed, Brenthy runs from source.
The source files are installed to a safe location where they are unlikely to be touched by other processes.
A dedicated Python virtual environment ([virtualenv](https://virtualenv.pypa.io/), consisting of a Python interpreter and modules (Python libraries) which Brenthy needs) is installed alongside the source code, which is the Python environment that runs Brenthy.
Using a dedicated Python environment avoids the problem of conflicting dependencies of modules which Brenthy needs and those installed by the OS.
Brenthy can of course still be run from source without being installed using the OS-global Python interpreter.
Instructions on how to do so are in [../User/RunningFromSource.md](../User/RunningFromSource.md)

## Purpose of Installation:
- to move Brenthy's source code out of the way
    - in a secure location safe from accidental or malicious threats
- to allow Brenthy to automatically start at system boot
- to allow Brenthy to automatically update itself
- to avoid conflicts between Brenthy's Python dependencies and those installed by the OS or user
- to allow the user to manage Brenthy as a standard OS-installed service (using standard tools such as systemd on Linux)

## Installation Procedure:
Brenthy's installation procedure can be started whenever it is [run from source](../User/RunningFromSource.md).

code: [Brenthy/run.py](/Brenthy/run.py)

Unless the `--dont-install` flag is passed when running Brenthy, Brenthy offers to install itself whenever it is run, prompting the user to type 'y' into the console if they want to.  
Brenthy will install itself without asking if the `--install` or `--install-dont-run` flags are passed.


Brenthy's installation manager has the following procedure:
_code: [Brenthy/install.py](/Brenthy/install.py)_
1. Assert that the current operating system is supported for installation.
2. Unless `--install` or `--install-dont-run` flags are passed, ask the user if Brenthy should install itself.
3. Check if Kubo (the most popular/best IPFS implementation) is installed, and if not ask the user whether to install it first (probably should, as Brenthy depends on IPFS).
4. Install IPFS by running the shell script corresponding to the OS located under [Brenthy/InstallScripts](/Brenthy/InstallScripts). For Linux systems running systemd, this is `Brenthy/InstallScripts/install_ipfs_linux_systemd.sh`
5. Execute the OS-compatible Brenthy installation shell script from `Brenthy/InstallScripts` to install Brenthy. For Linux systems running systemd, this script is `Brenthy/InstallScripts/install_brenthy_linux_systemd.sh`

The Brenthy installation shell script takes four parameters as input:
_code: [Brenthy/InstallScripts](/Brenthy/InstallScripts)_
  - `install_dir`: directory in which to install Brenthy
  - `data_dir`: the directory in which Brenthy should store its blockchain-types data
  - `python`: the path of the Python executable to use where it is needed in the installation process (the Brenthy program which is running this installation script provides the Python executable it is currently being run by)
  - `run_installation`: whether or not the installed Brenthy instance should be run after installation

The core installation procedure executed by the shell script is as follows:
1. Create the installation directory.
2. If the user specified a custom data-directory (the `data_dir` parameter), create a symlink from the default data-directory to the user-defined data-directory.
3. Copy Brenthy's source code (the very code that is currently running) to the installation directory.
4. Create an OS-user called `brenthy`.
5. Set file permissions on the installed source code and data directory, with the new `brenthy` user as owner.
6. Use the provided Python executable is used to create a Python virtual environment in the installation directory, and install all required Python modules there.
7. Register Brenthy as a service on the operating system, to be run at system boot by executing the installed Brenthy code using the installed Python virtual environment using the `brenthy` user. How this service registration is done depends on the operating system:
	- Linux with systemd: a systemd configuration file is created at `/etc/systemd/system/brenthy.service`
8. If the `run_installation` parameter was set to `true`, start the installed Brenthy service.
