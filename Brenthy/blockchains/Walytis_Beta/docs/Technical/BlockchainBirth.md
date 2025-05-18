_how the process of creating new blockchains works

Most blockchains today have one universal instance that gets born once when the developers are ready to launch it.
Since Walytis doesn't have a universal blockchain, but uses purpose-specific blockchains instead, creating blockchains is a common process.

## Birth Process
0. Walytis receives a [WalytisAPI request](WalytisAPI.md) from an, asking it to create a blockchain. 
1. Walytis sequentially creates five [chained](Block-Chaining.md) genesis blocks.
2.  The first block's IPFS CID becomes the new blockchain's ID. Walytis initialises the blockchain's machinery by creating its [appdata and block records database](StorageAndAppdata.md), i.e. writing the new blockchain's data to local storage, and by starting up its [networking](Networking.md).
3. Walytis enables processing WalytisAPI requests for the blockchain. The new blockchain is now ready to be used by applications, and can be [shared with other nodes](/docs/Technical/Joining.md).

## Genesis Block Properties
- The first block is of course special because it has no parents.
- The second block, having only the first block as its parent, is also irregular in that it contains only one parent, while normal block creation requires at least two parents for chaining security.
- All five automatically created genesis blocks have 'genesis' as a topic and don't have the blockchain ID as a topic. This makes their block IDs identifiable as genesis blocks, because all user-created blocks have the blockchain ID as the first topic.
- All genesis blocks have a _Hello World_ message and a random sequence of bytes as their block content.
- The genesis blocks do not trigger the new-block eventhandler of the Blockchain object in `walytis_api` to be called.
