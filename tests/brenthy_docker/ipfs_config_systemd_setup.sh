#!/bin/bash
# # Requires you to Enable IPv6 for docker containers
# # https://docs.docker.com/config/daemon/ipv6/
# echo '{
#   "ipv6": true,
#   "fixed-cidr-v6": "2001:db8:1::/64",
#   "experimental": true,
#   "ip6tables": true
# }' | sudo tee /etc/docker/daemon.json


set -e # exit on error

# the directory of this script
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


# IPFS Config Script
cp $SCRIPT_DIR/ipfs_config.sh /opt/ipfs_config.sh
chmod +x /opt/ipfs_config.sh
# create one-shot systemd service to run the IPFS initialisation script
echo "[Unit]
Description=IPFS node config
After=ipfs-init.service
Before=ipfs.service

[Service]
Environment=IPFS_PATH=/root/.ipfs
Type=oneshot
ExecStart=/bin/bash /opt/ipfs_config.sh

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/ipfs_config.service

# systemctl daemon-reload
systemctl enable ipfs_config
