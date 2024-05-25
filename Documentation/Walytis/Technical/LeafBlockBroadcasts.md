_When a blockchain is quiet, how do members coming online get the blocks they've missed out on?_

After creating a new block, Walytis nodes notify other nodes about it by broadcasting a message containing the new block's ID on a dedicated [IPFS publish-subscribe (pubsub)](https://blog.ipfs.tech/25-pubsub/) channel.
Upon receiving the message, the other nodes can download the block-file from IPFS and assimilate the block into the block records.

When a Walytis node goes online again after a period of being offline, it may have missed out on blocks that were published while it was offline.
So that such nodes don't have to wait until another peer publishes a new block for it to be able to catch up, Walytis has a system for regularly broadcasting the current leaf-blocks anew in times when no new blocks are being created.

Leaf-blocks are blocks with no children.
They are new blocks, the latest blocks created.
They cease being leaf-blocks when they become parent blocks of new blocks, which take over as the current leaf-blocks.

## Broadcasting Leaf-Blocks:

The goal of resending messages about already-published blocks is to keep the IPFS-pubsub communication channel for notifying nodes of new blocks active enough for nodes coming online to quickly get up-to-date with the current leaf-blocks even in times when no new blocks are being created .
In achieving this goal, we must ensure that we don't cause congestion to this broadcast channel.

In Walytis, this is achieved using the following loop that each node executes continuously during runtime:
- wait for a semi-random duration
- if no broadcast was received during that period, broadcast a message containing the list of the current leaf-blocks' IDs
The irregularity in the period of this loop prevents too many nodes from broadcasting these messages simultaneously.
To optimise the rate of occurrence of these broadcasts, the waiting duration is calculated from the addition of a constant and a random variable selected from a range proportional to the number of nodes on the network.

## Processing Leaf-Block Broadcasts

When a node receives a leaf-block broadcast, it checks if it knows the encoded blocks, and downloads and processes any that are new to it.
If the node has any newer leaf-blocks not included in the broadcast message, it waits for a semi-random duration as described above, after which it publishes its list of leaf-blocks if no other node has broadcast an up-to-date list of leaf-blocks in the meantime.

![](LeafBlocksBroadcasting.drawio.svg)