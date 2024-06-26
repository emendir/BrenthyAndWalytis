_blocks' components and how they work_
## Block Components
### Non-Metadata Block Components
- block content: data an application wants to store on the blockchain
- block-file: a file in which all of a block's components are encoded
### Block Metadata
- ipfs_cid: the IPFS content ID (i.e. a hash) of the block-file
- short_id: the short ID of the block (see [Short ID vs Long ID](./Blocks.md#short-id-vs-long-id) below)
- long_id: the long ID of the block (see [Short ID vs Long ID](./Blocks.md#short-id-vs-long-id) below)
- creator_id: the IPFS peer ID of the Walytis node that created this block
- creation_time: the date and time at which this block was created
- topics: the [topics](./Blocks.md#topics) which the application assigned to this block
- content_length: the length of the block's content (number of bytes)
- content_hash: a cryptographic hash of this block's content
- content_hash_algorithm: the algorithm used to generate the content hash
- parents: the short IDs of the parent blocks this block is chained to
- n_parents: the number of parent blocks
- parents_hash: a cryptographic hash for securing block lineage
- parents_hash_algorithm: the hashing algorithm used to generate the parents hash
- blockchain_version: the [Walytis Core Version](./WalytisVersioning.md#walytis-core-versioning) of the Walytis instance that created this block
### Short ID vs Long ID
The long block ID is the full identifier of a block.
As part of Walytis' unique chaining security, the block ID includes the entirety of a block's metadata, including the short IDs of its parent blocks.

A block's short ID includes all the block's metadata except for its parents' short IDs.
This is used to avoid the long block IDs growing longer with every generation, which is what would happen if each block ID were to encode the long IDs of its parent blocks.

### Block-File and the IPFS CID
All of a block's data, including its content and metadata except for its IPFS content ID (IPFS CID), is encoded into a file called the block-file.
The CID is a hash of the block-file, generated by IPFS to uniquely identify the file.

### Content
The block content is the piece data that the application wishes to store on the blockchain using the block.
Block content is in binary (array of bytes) so that any form of digital data can be encoded.
Walytis blocks have no limitations to the size of block content.
Practical limitations apply, though.

### Topics
This field is for application-defined metadata.
It is a list of strings, so multiple topics can be specified.
Because topics are part of the block ID, topics provide the ability to categorise/filter through blocks based on their ID without reading their content, providing efficient categorisation of / filtering through blocks.

![](BlockConstituents.drawio.svg)

### Hash Algorithms

Cryptographic algorithms are always at risk of losing their security if somebody finds a mathematical loophole in them or has access to new technologies such as feasible quantum computing.
To make it easy to transition to new cryptographic algorithms in the future, blocks specify the algorithm used to generate their parents-hash and the content hash.

## Mechanics
### Block Creation
When an application requests the creation of a new block on a specified blockchain, the blockchain proceeds in the following way:
  1. A list of parent blocks is made from recent blocks. 
  2. The block’s `creator_id` is set to the node’s IPFS peer ID and it’s `creation_time` is set to the current time.
  3. A cryptographic hash of the content is generated, forming the `content_hash`.
  4. The `parents_hash` is generated by hashing the parents' parents-hashes.
  5. The remaining metadata except the `ipfs_cid` is collected.
  6. The content and all metadata hitherto collected and generated are encoded into the block-file.
  7. The block-file is published on the IPFS network, generating its `ipfs_cid`.
  8. The block is stored in the local block records.
  9. The creator's Walytis node notifies other nodes about the new block by publishing its long ID on the IPFS pubsub channel dedicated to the blockchain.
10. The block is passed on to all interested locally running applications.

### Receiving New Blocks
Walytis nodes are informed of the existence of new blocks is by IPFS pubsub messages which contains the new block’s ID. This reception initiates the following procedure to incorporate the new block in the node's own block records:
1. The new block’s IPFS CID is extracted from the ID, and the block-file is downloaded from the IPFS network.
2. The block file-data is decoded, extracting metadata and content.
3. Block integrity checks are performed to make sure the block is valid:
    1. whether or not the newly decoded block’s ID is the same as what was published on pubsub
    2. whether or not the content length and hash match the content
    3. whether or not the block's parents-list conforms to the chaining rules
    4. whether or not the Walytis node knows all the parent blocks (if not, the block is put on stand-by (not yet approved) until all the blocks’ parent blocks have been found, integrity-checked, approved and passed to their apps (i.e. completely processed according to this description))
4. The block is stored in the local blocks records.
5. The block is passed on to all interested locally running applications.
