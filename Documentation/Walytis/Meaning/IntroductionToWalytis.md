![](../../../Graphics/WalytisIcon.svg)

# Walytis

___A flexible, lightweight, nonlinear blockchain. Built to be built upon.___

_`4D61646520776974682073696E63657265206C6F766520666F72206D616E6B696E642E`_

Walytis is a type of blockchain that is nothing more than a fully distributed database-management system with a focus on accessibility, flexibility and lightweightedness, when compared to other blockchains.
Applications can create a new Walytis blockchain (i.e. a new database) whenever they need one.
While they can always add new data to it, existing data can never be deleted or modified.

Walytis was designed with a few essential criteria in mind to improve upon existing blockchains: no energy wasting, no block creation competition and no block time.
Along the journey of its initial development, countless cool features were invented and added to improve its flexibility, usability and security.

One of the defining features of Walytis is that blocks can be added to blockchains instantly.
This necessarily leads to a nonlinear blockchain structure, with is like a tree in which the branches regrow into each other, forming an unordered mesh of block relationships.

Since Walytis is lightweight and flexible, it is feasible for every application _to have its own blockchain_, or even to create and use multiple blockchains if they need to.
This stands in stark contrast to most existing blockchains, which instead have only one universal instance of the blockchain existing in which all applications take a tiny part.

Because Walytis is resource-efficient, Walytis also has the advantage of obsoleting miners (classical blockchains' men-in-the-middle, who provide access to the blockchains to their users), because most devices, even smartphones, can take part directly in running a blockchain, or even several blockchains.

Another non-feature is that there is no tokenisation or any form of finance involved.
No financial entry barrier, no forces of incentivisation, no human stress or worry which such systems lead to.
This allows new users to jump right in and start using this blockchain easily, simply as the piece of infrastructure it was designed to be.

To gain a deeper understanding of Walytis' unique properties and how it differs from conventional blockchains, see [Understanding Nonlinear Blockchain](./UnderstandingNonlinearBlockchain.md).
## Features
_A list of the most significant features that set this blockchain apart from classical blockchains such as Bitcoin and Ethereum_
- flexible: applications can create a blockchain for any use-case they have
- no block time: blocks can be added instantly
- no block competition: no uncertainty whether a block you're trying to add to the blockchain will make it
- no mining
	- completely decentralised, no hierarchy in participant nodes
	- no wasting resources for proof of work
	- every blockchain user is a full node in the blockchain
- lightweight and resource-efficient: A full node can comfortably be run on a smartphone or Raspberry Pi (not that there are any node types other than full). Shall we test an Esp32 microcontroller running Linux next?
- no tokenisation or other financioid systems built in
- accessibility: To get started, users only need to install the software. They can then immediately start using it and building on it in Python, one of the most popular programming languages (support for other languages should be relatively easy to build) 

### Virtual Blockchains
The features of Walytis blockchains can be expanded by building modules on top of it that provide applications with virtual blockchains that have unique features which aren't built into Walytis.

I'm working on a few that provide the following features:
- Mutability: a distributed database in which blocks can be edited and their edit-history read
- Privacy: a distributed database in which the application's content is encrypted and stored off-chain, and blocks are authenticated by having their creators sign them

These modules can be compounded to combine their features.
Underneath, the blockchains are still Walytis blockchains of course, but because these modules abstract away from applications the mechanics of creating mutable content or authenticating blocks, I call the interface they provide to applications 'virtual blockchains'.

## Applications: Examples of Use Cases
Here is a list of some applications that are currently under development to explain by example how Walytis blockchains might be used:
- Messenger:
	- A blockchain can be used to record the existence of messages in a chatroom. Actual message content is stored off-chain for privacy. In this case the blockchain is used not for storage but to help the various devices of the member's chatroom coordinate their data synchronisation.
- File Synchronisation:
	- File changes are recorded in blocks, creating a complete unified history of file edits across users. Actual files are stored off-chain for storage-efficiency.
- Serverless Git Collaboration:
	- Ever notice that git already looks like a blockchain? Map git commits onto Walytis blocks and git repositories onto Walytis blockchains and you've got a shared git repo!

## Security
Walytis does not rely on the [original proof-of-work concept of security invented by Satoshi Nakamoto](https://bitcoin.org/bitcoin.pdf), nor on any adaptations of this such as Ethereum's [proof-of-stake](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/).
Instead of constantly sharing and comparing different versions of blockchain histories over the network and accepting the longest valid version, each node relies on its own stored record of blocks.
This means that in Walytis, security against the creation of fake versions of the blockchain history (chain of blocks) lies not in consensus algorithms that constantly decide anew on the accepted blockchain history as in classical blockchains, instead it lies to a large extent in the memory of the blockchain history stored on each blockchain node.
Attackers aren't likely to attempt to hack every node on the network and edit each node's block history.
They're probably more likely to try to find loopholes in the integrity verification systems in Walytis' blockchain logic.

Local block storage isn't all that provides security in Walytis.
Like most blockchains, it relies heavily on the cryptographic chaining of blocks.
To learn how this works in Walytis, read [The Walytis Blockchain-Architecture Security](WalytisBlockchainSecurity.md).

## Techy Details:
To gain a full understanding of how Walytis works, check out the [overview of the technical documentation](../../DocsOverview.md#brenthy---technical).

Here are some of the highlights:
### Communication
In this blockchain, nodes communicate to each other via the [InterPlanetary File System, IPFS](https://ipfs.tech).
They store blocks as files on IPFS and notify each other about new blocks using [IPFS' experimental pubsub feature](https://blog.ipfs.tech/25-pubsub/).

### Application Interface
The core Walytis software runs on an operating system as a background service that listens on a local network port for incoming API requests.
Applications use a simple library called `walytis_api` to communicate with the blockchains being run by the Walytis software.
Assuming Walytis automatically runs whenever its host computer starts up, it can still communicate with other nodes and receive information for the applications even when the applications aren't running.

Currently, `walytis_api` is implemented in Python, but due to its simplicity and small size it should be fairly straight-forward to translate it into other languages.



## Running Walytis
Walytis is run by [Brenthy](/Documentation/Brenthy/Meaning/IntroductionToBrenthy.md), a framework for developing and deploying new kinds of blockchains.
Walytis comes preinstalled with Brenthy, so simply follow the instructions from Brenthy's [installation](InstallingBrenthy.md) or [running-from-source](../../Brenthy/User/RunningFromSource.md) guides to install or run it.

### What Exactly is Brenthy?
Brenthy and Walytis run together.

Walytis includes all the blockchain-related machinery, such as:
- creating, receiving, verifying and storing blocks
- communicating with other peers

Brenthy handles all the rest of the machinery needed to make Walytis run on a computer, such as:
- interaction with the local operating system (installation, running on startup)
- automatic updates of itself and Walytis
- [BrenthyAPI](/Documentation/Brenthy/Technical/BrenthyAPI.md), the API infrastructure which applications use to interact with Walytis

Brenthy & Walytis were initially developed as a single project.
The blockchain machinery (Walytis) was split off from the rest (Brenthy) to allow that rest to be used to run other types of blockchains, facilitating blockchain inventors in the development of new kinds of blockchains.
Now, Brenthy can run other types of blockchains at the same time as Walytis.

## Walytis' Source Code
Because Brenthy and Walytis depend on each other, they share the same repository. 
The source code for Walytis is located under [/Brenthy/blockchains/Walytis_Beta](/Brenthy/blockchains/Walytis_Beta/ReadMe.md)
