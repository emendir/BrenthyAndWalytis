# # Requires you to Enable IPv6 for docker containers
# # https://docs.docker.com/config/daemon/ipv6/
# echo '{
#   "ipv6": true,
#   "fixed-cidr-v6": "2001:db8:1::/64",
#   "experimental": true,
#   "ip6tables": true
# }' | sudo tee -a /etc/docker/daemon.json


# IPFS router mercy: limit IPv4 communication
echo "## Limit IPv4 communication to reduce number of peers
ipfs config --json Swarm.AddrFilters '[\"/ip4/0.0.0.0/ipcidr/0\"]'

## disable TCP communications
#ipfs config --json Swarm.Transports.Network.TCP false
#ipfs config --json Swarm.Transports.Network.Websocket false
" >> /opt/ipfs_router_mercy.sh
chmod +x /opt/ipfs_router_mercy.sh
# create one-shot systemd service to run the IPFS initialisation script
echo "[Unit]
Description=IPFS router mercy config
After=ipfs-init.service
Before=ipfs.service

[Service]
Type=oneshot
ExecStart=/bin/bash /opt/ipfs_router_mercy.sh

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/ipfs_router_mercy.service

systemctl daemon-reload
systemctl enable ipfs_router_mercy