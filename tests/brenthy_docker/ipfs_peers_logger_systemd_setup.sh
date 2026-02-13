#!/bin/bash
set -e # exit on error

# the directory of this script
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


# IPFS peer logging script
cp "$SCRIPT_DIR"/ipfs_peers_logger.py /opt/ipfs_peers_logger.py
echo "[Unit]
Description=Log IPFS peer connections
DefaultDependencies=no
After=ipfs.service

[Service]
Type=simple
ExecStart=/opt/Brenthy/Python/bin/python3 /opt/ipfs_peers_logger.py
RemainAfterExit=true
Restart=always

[Install]
WantedBy=basic.target
" | tee /etc/systemd/system/ipfs_peers_logger.service

# systemctl daemon-reload
# systemctl enable ipfs_peers_logger

if ! [ -e /etc/systemd/system/basic.target.wants/ ];then
    mkdir /etc/systemd/system/basic.target.wants/
fi
ln -s /etc/systemd/system/ipfs_peers_logger.service /etc/systemd/system/basic.target.wants/ipfs_peers_logger.service
