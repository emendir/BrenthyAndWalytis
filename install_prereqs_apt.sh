#!/bin/bash

# the absolute path of this script's directory
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPT_DIR

set -e # Exit if any command fails


## PYTHON
sudo apt install -y python3-virtualenv python3-pip python-is-python3 

## DOCKER
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt remove $pkg; done

# Add Docker's official GPG key:
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update

sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin



# Create the docker group if it doesn't exist
if ! getent group docker > /dev/null; then
  echo "Creating docker group..."
  sudo groupadd docker
else
  echo "Docker group already exists."
fi

# Add current user to docker group if not already a member
if id -nG "$USER" | grep -qw docker; then
  echo "User $USER is already in the docker group."
else
  echo "Adding user $USER to docker group..."
  sudo usermod -aG docker $USER
  echo "You may need to log out and log back in for group changes to take effect."
fi

# Docker daemon configuration for IPv6
DAEMON_JSON="/etc/docker/daemon.json"
IPV6_CONFIG='"ipv6": true'

if sudo grep -q "$IPV6_CONFIG" "$DAEMON_JSON"; then
  echo "IPv6 is already configured in $DAEMON_JSON."
else
  echo "Configuring IPv6 for Docker..."
  sudo tee -a "$DAEMON_JSON" > /dev/null <<EOL
{
  "ipv6": true,
  "fixed-cidr-v6": "2001:db8:1::/64",
  "experimental": true,
  "ip6tables": true
}
EOL
  echo "IPv6 configuration added. Restart Docker for changes to take effect."
fi


## IPFS
./Brenthy/InstallScripts/install_ipfs_linux_systemd.sh

