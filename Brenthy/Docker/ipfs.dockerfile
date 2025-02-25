FROM ipfs/kubo:latest
COPY ipfs_brenthy_config.sh /container-init.d/ipfs_brenthy_config.sh

CMD ["daemon", "--migrate=true", "--agent-version-suffix=docker", "--enable-pubsub-experiment"]