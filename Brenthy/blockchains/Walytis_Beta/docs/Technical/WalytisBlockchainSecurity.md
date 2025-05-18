_the mechanisms built into Walytis to preserve blockchains' data integrity_
# The Walytis Blockchain-Architecture Security

_Let's structure this analysis of the features that ensure the integrity of the Walytis blockchain by first clearly defining what Walytis is, what its purpose is, and how it manifests its purpose, then identifying the theoretical risks that threaten the fulfilment of this purpose, and finally by analysing the consequences of each risk and the countermeasures taken in the architecture of Walytis against those risks._

As a blockchain, Walytis serves the specific purpose of:
- providing a distributed database
- in which participants can add data and access all data ever added to it,
- while preserving some sense of the chronological order in which data was added.


Let's look at how Walytis achieves these specifications, and identify the security risks in these methods:
- **Providing a distributed database:** Every node in a Walytis blockchain locally stores a copy of each block on the blockchain, and provides access to it via the Walytis API.
  - Risks:
    - availability attacks
    - data loss/corruption
- **Adding data and ensuring all nodes have all data ever created:** Walytis uses [IPFS](https://ipfs.tech) and IPFS-PubSub to share new blocks between peers.
  - Risks:
    - content deletion
    - node communication jamming
    - IPFS content forgery
    - IPFS content corruption
- **Preserving chronology:** Walytis blocks contain the block IDs of blocks created shortly before themselves (parent blocks).
  - Risks:
    - block chronology forgery

## Risks & Countermeasures
### Availability Attacks
Since all data is stored on every node, denying availability to a node would require hacking the the desired node's computer to deny availability to or by spamming it with communications (see [Node Communication Jamming](#node-communication-jamming)).
Absolute availability failure would mean taking down every node on the network, which depending on the size of the network could be an astronomical challenge.

The difficulty of targeted attacks on individual nodes depends on the robustness of the actual Brenthy and Walytis software.


### Node Data Loss and Corruption
#### Data Loss
The chronology system of Walytis ensures that blocks can't be forgotten (see [Block Chronology Forgery](#block-chronology-forgery) for security details).
It also ensures that data loss cannot go unnoticed.
In the case of data loss, nodes can retrieve the lost data from other nodes (see [Node Communication Jamming](#node-communication-jamming) for security details).

#### Data Corruption

_Consequences:_  
Data corruption would, if unchecked, lead to a Walytis node providing any kind of false information to applications in the worst of cases, and crashing in the best.

_Countermeasures:_  
- **Each block's data is stored in a strictly encoded block-file.**
- **A block's ID comprises of a hash of the block-file, a hash of the block content, a hash of its parent blocks and the block's metadata** (creation time, creator ID etc; see [Blocks](Blocks.md) for full details).

This way, corruption is extremely unlikely to go unnoticed.

**Due to their built-in data-sharing, Walytis nodes have natural self-healing capabilities for their storage. However, these have not been thoroughly tested.**

### Content Deletion
Every node on the network locally stores a copy of each block, and shares it to the world via IPFS.
So to delete a block from the blockchain, one would have to delete that block-file on every computer in the network by hacking each one, which depending on the network size, could be an astronomical challenge.

An alternative to block deletion is block forgetting, ie. trying to trick the nodes into forgetting a certain block exists on the blockchain.
However, the blockchain's block-chaining creates a living record of all blocks created.
See [Block Chronology Forgery](#block-chronology-forgery) for details on that mechanism.

### Node Communication Outages
Walytis uses IPFS-pubsub to allow nodes to notify each other of newly created blocks.

_Consequences:_
Unreliable broadcasts on the IPFS-pubsub channel would prevent some nodes from being notified of new blocks.

_Countermeasures:_
- **New blocks encode in them the IDs of older blocks recently created before them**, and **new blocks are only assimilated by nodes if all their parent blocks already have been**. Thus, if a node were to miss the notification of a block, it would learn about it when processing its children blocks.
- **When the pubsub communications channel is quiet because no new blocks are being created, nodes broadcast lists of their leaf-blocks (newest blocks without children) to each other**. This provides constant redundancy for each message published on this communications channel. Learn more under [Leaf-Block Broadcasts](LeafBlockBroadcasts.md)
### Node Communication Jamming
Walytis uses IPFS-pubsub to allow nodes to notify each other of newly created blocks.

_Consequences:_  
Jamming the communication between nodes would lead them to be unable to share newly created blocks, meaning not all nodes would know of all blocks, which also has the consequence of weakening the blockchain's chronology preservation system because new blocks can no longer reference each other as parents.

_Countermeasures:_ 
Communication overload e.g. by spamming PubSub channels with enormous amounts of information is currently a known weakness.
**Spam filtering systems need to be developed against this weakness.**

### Block Corruption and Forgery
In Walytis, blocks are encoded into block-files which are shared between nodes via IPFS.
We can't rely with complete confidence on IPFS' storage capability, because theoretically two different files could have the same content ID (CID), because on IPFS every file's ID is the hash of its content.
This makes room for counterfeit or corrupted block-files to be spread on the network.

It must be noted that deliberately spreading counterfeit copies of existing IPFS content on the network is a challenge in it's own right, as IPFS is designed to distribute content autonomously in a decentralised way.

In this analysis, we'll use the term _corruption_ to mean replacing readable data with unreadable data, and _forgery_ to mean replacing readable data with other readable but false data.

Blocks can be corrupted at two levels:
- [Block-file corruption:](#block-file-corruption) This is the easiest case to produce deliberately and the most likely case to occur accidentally. Some unreadable file on IPFS has the same CID as a block-file. The block and its children become unavailable to nodes who have the corrupted block-file. 
- [Block content corruption/forgery:](#block-content-forgery-and-corruption) In this case the disturbing file is valid block-file that matches a different block's ID but has different block-content. Nodes can add the corrupted block to their database, but the applications see false content which is either unreadable to them (corruption) or readable but false (forgery) 
- [Block parents corruption:](#block-chronology-forgery) In this case the disturbing file is valid block-file that matches a different block's ID but has different parents.

#### Block-File Corruption
_Consequences:_  
The consequences of block corruption are varied, depending on what kind of data shares the same IPFS CID:
- Unrelated IPFS content exists with the same CID as a block file: Nodes who receive the corrupted/false block file before they get the real one would be unable to read the block.
- Different block IDs have different valid block files with the same CID: each node will only have exactly one of the two blocks, and none of the other's children
- Same block with different valid block-files having the same CID: The only content of the block-files that isn't in the block ID is the block content and the block parents. See [Block Content Forgery and Corruption](#block-content-forgery-and-corruption) and [Block Chronology Forgery](#block-chronology-forgery).

_Countermeasures:_  
- **A block's ID includes a hash of its block-file (its IPFS CID)**
- **Block-files and IDs follow a strict format (see [Blocks](Blocks.md)), where all data in the files is either included as-is in the block ID or has a hash included in the block ID**. This makes it difficult and in some cases impossible to forge different valid block-files for the same block ID, as many constraints must be satisfied.
- **Before publishing, blocks are regenerated if IPFS content with the same CID already exists.**
Regeneration means the timestamp is changed and a new CID is generated.
This avoids creating blocks with the same CIDs of known already existing IPFS content.
- If a node were to try and fail to load a block from a corrupted block-file, it would **delete the corrupted block-file from its IPFS storage** to reduce the distribution of the corrupted block-file on the IPFS network.


#### Block Content Forgery and Corruption

_Consequences:_  
Applications would see false content which is either unreadable to them (in the case of simple corruption) or readable but false (in the case of forgery)
 
_Countermeasures:_
- **A hash of the content is encoded in the block ID**.
- **The content size is encoded in the block ID**.

Explanation:

Multiple different pieces of data could have the same hash.

This is extremely unlikely to be a problem, because for two different contents to be valid given a block's ID, they have to follow the following constraints:
- they would have to have the same content hash
- they would have to produce the same block-file hash (IPFS CID) when encoded into a block-file
- they would have to be the same length

And of course, in the case of forgery, finding counterfeit content that is also useful at an application level makes it even more difficult!

For small block content, e.g. content shorter than the hash lengths, alternative block contents will be impossible.

**We should do a mathematical analysis of how difficult such forgery or how unlikely such accidents are expected to be.**

Also, should more effective hashing algorithms be developed, **Walytis has the capability to migrate to new hashing algorithms in living blockchains!**
 

### Block Chronology Forgery

The chaining of blocks on a blockchain allows for a chronological order of block creation to be proved and ensures that no blocks can ever be forgotten.

_Consequences:_  
If a malicious actor were able to claim a block has different parent blocks than it really has, they would be able to make it look as if a block was created earlier than it really was or stop some nodes from knowing a certain block exists.

_Countermeasures:_  
Parent blocks' full IDs aren't encoded into block IDs, otherwise IDs would grow in length endlessly with every generation.
Therefore, in a block's _long ID_, we encode the _short ID_ of its parent blocks, which is the same as the long ID except that it doesn't contain it's parents' short IDs.

Originally (now deprecated), I had the parent ID referenced in the block short ID by a cryptographic hash.
Securely referencing other blocks via hashes is a lot more difficult than securely referencing block content, though.
If we secured them like block content by adding the hash of a block's parents' block IDs to its block ID, forging parents would be easier than it is to forge useful content, because with the parents we'd have hashes referencing IDs with hashes referencing IDs with hashes and so on, which leaves a huge amount of space for inventing new blocks and block histories that satisfy a given hash.
The block ID has too many fields (such as creation-time and topics) which can be tuned to produce a specific hash without jeopardising the validity of the new block.

The solution is that the parents-hash shouldn't be a hash of entire parents' block IDs, but only parents' parents-hashes.
**The parents-hash is encoded into the block ID. The genesis block produces a random parents-hash, and all subsequent blocks produce their parent hashes by hashing only the combination of the parents-hashes of their parent blocks.**

We can reduce the probability of the existence of different combinations of parent blocks producing the same parents-hash by adding a rule that **for a given set of parent blocks, none of the parents may be an ancestor of one of the others, unless only a single parent is available, in which the genesis block must be included**.
We can further reduce the probability of the same block ID having different valid combinations of parents if we **encode the number of parent blocks in the block ID** alongside the parents-hash.
We can reduce this probability even further by requiring that **parent blocks be sorted when hashing their parents-hashes**.

Having significantly reduced the probability of the ability of the same parents-hash to refer to different parents by chance, the only problem left is the deliberate generation of different pairs of parents that have the same hash.

A forger must generate a history of (most likely) huge numbers of blocks until a block with the desired parents' hash is produced.
Then, they must forge a valid block file including those generated parents, satisfying all the constraints listed in [Block Corruption](#block-file-corruption).

**We should do a mathematical analysis of how difficult such a task would be expected to be.**
It should be at an astronomical order of magnitude.

If not, **we could build a monitoring system for detecting such forgery via large numbers of parent blocks that are isolated from the rest of the blockchain**.
