If we can't connect to the docker containers via IPFS (test gets stuck after printing `Genesis block`), restart the docker daemon and IPFS to ensure docker has its networking configured properly and that IPFS is using docker's virtual network interface card:

```sh
sudo systemctl restart docker
sudo systemctl restart ipfs
```

Also, sometimes I need to manually delete old docker containers:
```sh
docker rm $(docker ps -aq)
```

### Logs
The logfile for the test-script's docker instance is in the user's appdata.
E.g. on most linux systems, this is HOME/.local/share/Brenthy/Brenthy.log