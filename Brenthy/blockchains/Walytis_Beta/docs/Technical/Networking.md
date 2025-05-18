_the different ways in which Walytis nodes communicate with each other_

Walytis uses the [Interplanetary Filesystem (IPFS)](https://ipfs.tech) and its built-in [libp2p](https://libp2p.io) peer-to-peer communications engine to allow nodes to communicate with each other.

## Used Communication Methods

Walytis nodes communicate with each other in two different ways for different purposes:
- **IPFS Files:** Using [IPFS' main feature of decentralised file storage](https://docs.ipfs.tech/how-to/desktop-app/#add-local-files), nodes store and share blockchains' blocks' datafiles.
- **IPFS-PubSub:** Using the [publish-subscribe feature built into IPFS' libp2p](https://blog.ipfs.tech/25-pubsub/), nodes notify each other of newly created blocks.
- [IPFS-DataTransmission](https://github.com/emendir/ipfs-toolkit-python?tab=readme-ov-file#ipfs-datatransmission): Using TCP websockets via which IPFS creates point-to-point tunnels between two peers ([libp2p-stream-mounting](https://github.com/ipfs/kubo/blob/master/docs/experimental-features.md#ipfs-p2p)), joining nodes download the data they need from blockchain nodes.
![](./Dataflow.drawio.svg) 

## Communicative Processes:
### Block Creation

- When a node creates a new block, it encodes all the block's data and metadata into the _block data-file_, which it publishes on IPFS, which assigns it a unique content identifier (CID), which becomes part of the block's ID.
- The node then publishes a message containing the block's ID on a pubsub channel which all nodes on the blockchain are subscribed to.
- When another node receives the pubsub message with the ID of the new block, it extracts the block's CID from the block ID encoded in the message and uses IPFS' file-sharing to retrieve the block's datafile from one of the other nodes.
### Quiet Blockchain

_See [Leaf-Block Broadcasts](LeafBlockBroadcasts.md) for more details._

When the pubsub communications channel is quiet because no new blocks are being created, nodes broadcast lists of their leaf-blocks (newest blocks without children) to each other to ensure redundancy in the pubsub messages and enable nodes coming online to get up-to-date with the newest blocks quickly.

### Blockchain Joining

_See [Joining](./Joining.md) for more details_.

Blockchain nodes listen for incoming join requests on an IPFS libp2p-stream-mounting websocket named `/x/BLOCKCHAIN_ID:JoinRequest`. We'll call this websocket and the part of Walytis which processes incoming communications on the _join-request-listener_.
When a node wants to join a blockchain using an invitation, it extracts the IPFS peer IDs encoded in the invitation. It connects to each peer's join-request-listener, asking to join the blockchain, until one of them responds and transmits, over the same connection, its blockchain appdata.
