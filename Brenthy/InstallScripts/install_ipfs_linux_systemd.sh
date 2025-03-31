#!/bin/bash

IPFS_VERSION="0.22.0"
# the threshold of RAM in gigabytes under which the lowpower profile is applied
LOW_POWER_RAM_GB=6
# Get the CPU architecture using uname
ARCH=$(uname -m)

# Initialize the variable to store the architecture string
ARCH_STRING=""

# Check the architecture and set the variable accordingly
if [ "$ARCH" == "i386" ] || [ "$ARCH" == "i686" ]; then
    ARCH_STRING="386"
elif [ "$ARCH" == "x86_64" ]; then
    ARCH_STRING="amd64"
elif [ "$ARCH" == "armv7l" ]; then
    ARCH_STRING="arm"
elif [ "$ARCH" == "aarch64" ]; then
    ARCH_STRING="arm64"
else
    echo "Unknown architecture: $ARCH"
    exit 1
fi



ZIP_NAME="kubo_v${IPFS_VERSION}_linux-${ARCH_STRING}.tar.gz"
wget "https://dist.ipfs.tech/kubo/v${IPFS_VERSION}/${ZIP_NAME}"
tar -xvzf $ZIP_NAME
cd kubo
sudo bash install.sh

# clean up
cd ..
rm -r kubo
rm $ZIP_NAME

if [ "$(ipfs --version)" = "ipfs version ${IPFS_VERSION}" ]; then
  ipfs init
  
  ## Configure IPFS
  ipfs config --json Experimental.Libp2pStreamMounting true
  
  # Get total memory in kibibytes, then convert to gibibytes
  total_memory_kb=$(free -k | awk '/^Mem:/ {print $2}')
  total_memory_gb=$((total_memory_kb / 1024 / 1024))

  if [ "$total_memory_gb" -lt "$LOW_POWER_RAM_GB" ]; then
    echo "Applying low-power profile..."
    ipfs config profile apply lowpower
  fi
  
  
  echo "[Unit]
Description=InterPlanetary FileSystem - the infrastructure of a P2P internet

[Service]
User=$USER
Environment=LIBP2P_TCP_REUSEPORT=false
ExecStart=ipfs daemon --enable-pubsub-experiment
Restart=always

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/ipfs.service
  sudo systemctl enable ipfs
  sudo systemctl start ipfs
  echo "Installation of IPFS finished!"
else
  RED='\033[0;31m'
  NC='\033[0m'  # No Color

  echo -e "${RED}Installation of IPFS failed!!.${NC}"
fi


