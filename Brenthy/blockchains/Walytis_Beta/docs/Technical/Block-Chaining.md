_how blocks are chained in Walytis_
## Nonlinear Chaining
_For a deeper understanding of what implications non-linear chaining has for Walytis, see [Understanding Nonlinear Blockchains](/Documentation/Walytis/Meaning/UnderstandingNonlinearBlockchain.md)._

In Walytis, each block ID (except for the first two genesis blocks) contains a reference to at least two other older blocks, called its parents.
This differs from most existing blockchains, where each block contains a reference to exactly one parent block, forming a linear chain.
Let's call blockchains in which blocks have multiple parents and multiple children nonlinear.

The reason why Walytis is nonlinear is to allow for different blocks to be created by different nodes simultaneously.
If blocks can be created simultaneously, different blocks can have the same parent, meaning a block can have multiple children.
If blocks can have multiple children, blocks should also be able to have multiple parents to avoid the isolation of branches in the chain.

In Walytis, for chaining security reasons, none of the parents may be an ancestor of any of the others, unless only a single parent is available, in which the genesis block must be included as a parent.
To understand the reason for this, and the reasons behind all other aspects of Walytis' unique way of chaining blocks, read the documentation on [Walytis' blockchain-architecture security](./WalytisBlockchainSecurity.md#block-chronology-forgery).

## ID-Chaining

Parent block IDs aren't encoded into block IDs, otherwise IDs would grow in length endlessly with every generation.
In a block's _long ID_, we encode the _short ID_ of its parent blocks, which is the same as the long ID except that it doesn't contain the parent short IDs.
The block short ID does however encode the number of parents a block has.

## Parents-Hash

Despite not containing the parent block short IDs, a block's short ID still needs to contain some form of a cryptographic reference to its parents to secure the full chaining lineage of the blockchain.
To this end, the short ID of a block contains a field called the parents-hash, which is the cryptographic hash of the block's parents' parents-hashes.
For the genesis block, this is set to random data because it has no parents.
Read more about this in [Walytis' Blockchain-Architecture Security](./WalytisBlockchainSecurity.md#block-chronology-forgery).
