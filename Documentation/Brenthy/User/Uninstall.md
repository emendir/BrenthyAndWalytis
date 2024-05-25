_How to uninstall Brenthy._

# Uninstalling Brenthy

No programmatic uninstaller has been built yet.
Uninstalling Brenthy is pretty easy, though, and is performed in two parts:
- uninstalling Brenthy itself
- uninstalling IPFS, if desired (IPFS is installed by Brenthy during installation if it isn't already)

## Uninstall Brenthy
1. Stop Brenthy. On Linux running systemd:
	```sh
	sudo systemctl stop brenthy
	```
2. Delete the following:
	- Brenthy installation directory (`/opt/Brenthy` by default on Linux)
	- the Brenthy service registration (the `/etc/systemd/system/brenthy.service` file on Linux running systemd)

## Uninstall IPFS
- delete the IPFS binary (`/usr/local/bin/ipfs` by default on Linux)
- delete your IPFS repo (folder containing all your IPFS data): `~/.ipfs` by default
- delete the the IPFS service registration (the `/etc/systemd/system/ipfs.service` file on Linux running systemd as configured by the Brenthy installer)
