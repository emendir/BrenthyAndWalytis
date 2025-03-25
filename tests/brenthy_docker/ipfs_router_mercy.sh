# # Requires you to Enable IPv6 for docker containers
# # https://docs.docker.com/config/daemon/ipv6/
# echo '{
#   "ipv6": true,
#   "fixed-cidr-v6": "2001:db8:1::/64",
#   "experimental": true,
#   "ip6tables": true
# }' | sudo tee /etc/docker/daemon.json


# IPFS router mercy: limit IPv4 communication
echo "## Limit IPv4 communication to reduce number of peers
ipfs config --json Swarm.AddrFilters '[\"/ip4/32.0.0.0/ipcidr/3\",\"/ip4/16.0.0.0/ipcidr/4\",\"/ip4/0.0.0.0/ipcidr/5\",\"/ip4/12.0.0.0/ipcidr/6\",\"/ip4/8.0.0.0/ipcidr/7\",\"/ip4/11.0.0.0/ipcidr/8\",\"/ip4/64.0.0.0/ipcidr/3\",\"/ip4/96.0.0.0/ipcidr/4\",\"/ip4/112.0.0.0/ipcidr/5\",\"/ip4/120.0.0.0/ipcidr/6\",\"/ip4/124.0.0.0/ipcidr/7\",\"/ip4/126.0.0.0/ipcidr/8\",\"/ip4/128.0.0.0/ipcidr/3\",\"/ip4/176.0.0.0/ipcidr/4\",\"/ip4/160.0.0.0/ipcidr/5\",\"/ip4/168.0.0.0/ipcidr/6\",\"/ip4/174.0.0.0/ipcidr/7\",\"/ip4/173.0.0.0/ipcidr/8\",\"/ip4/172.128.0.0/ipcidr/9\",\"/ip4/172.64.0.0/ipcidr/10\",\"/ip4/172.32.0.0/ipcidr/11\",\"/ip4/172.0.0.0/ipcidr/12\",\"/ip4/224.0.0.0/ipcidr/3\",\"/ip4/208.0.0.0/ipcidr/4\",\"/ip4/200.0.0.0/ipcidr/5\",\"/ip4/196.0.0.0/ipcidr/6\",\"/ip4/194.0.0.0/ipcidr/7\",\"/ip4/193.0.0.0/ipcidr/8\",\"/ip4/192.0.0.0/ipcidr/9\",\"/ip4/192.192.0.0/ipcidr/10\",\"/ip4/192.128.0.0/ipcidr/11\",\"/ip4/192.176.0.0/ipcidr/12\",\"/ip4/192.160.0.0/ipcidr/13\",\"/ip4/192.172.0.0/ipcidr/14\",\"/ip4/192.170.0.0/ipcidr/15\",\"/ip4/192.169.0.0/ipcidr/16\"]'

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