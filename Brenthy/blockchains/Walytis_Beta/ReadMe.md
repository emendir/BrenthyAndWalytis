![](/graphics/WalytisIcon.png)



# [Walytis](/docs/Meaning/IntroductionToWalytis.md)

**_A flexible, lightweight, nonlinear blockchain. Built to be built upon._**
_`4D61646520776974682073696E63657265206C6F766520666F72206D616E6B696E642E`_

Walytis is a database-blockchain, a type of blockchain that is nothing more than a fully distributed database-management system, with a focus on accessibility, flexibility and lightweightedness, when compared to other blockchains.
Applications can create a new Walytis database-blockchain whenever they need one.
While they can always add new data to it, existing data can never be deleted or modified.

## Applications: Examples of Use Cases

- [Messenger](https://github.com/emendir/Endra): A database-blockchain can be used to record the existence of messages in a chatroom. Actual message content is stored off-chain for privacy. In this case the database-blockchain is used not for storage but to help the various devices of the member's chatroom coordinate their data synchronisation.
  
- File Synchronisation: File changes are recorded in blocks, creating a complete unified history of file edits across users. Actual files are stored off-chain for storage-efficiency.
  
- Serverless Git Collaboration: Ever notice that git already looks like a blockchain? Map git commits onto Walytis blocks and git repositories onto Walytis blockchains and you've got a shared git repo!
  
- [Identity Management](https://github.com/emendir/WalytisIdentities): One data-base blockchain is used for every identity, publishing [DID-documents](https://www.w3.org/TR/did-1.0/) as blocks, cryptographically authenticated
  

### Blockchain Overlays

The features of Walytis blockchains can be expanded by building modules on top of them that provide applications with interfaces to database-blockchains that have unique features and functionality not built into Walytis.
Currently under development are tools for off-chain and encrypted data storage, authentication, access-control, identity-management and mutable data structures are built in a modular way so that application developers can choose which extra features they need for their use case. These modules can be compounded to combine their features.


Learn about Walytis here: [Introduction to Walytis](/docs/Meaning/IntroductionToWalytis.md)  
Learn why Walytis was developed: [Walytis' Rationale](/docs/Meaning/WalytisRationale.md)  


## Getting Started

### Install or Run from Source

Install Walytis to run on your system as a background service using [Brenthy](https://github.com/emendir/BrenthyAndWalytis/):

Ubuntu quick start:

```sh
# install prerequisites
sudo apt update && sudo apt install -y python3-virtualenv git

# download BrenthyAndWalytis
git clone https://github.com/emendir/BrenthyAndWalytis
cd BrenthyAndWalytis

# set up python environment (you can skip this if you only want to install)
virtualenv .venv && source .venv/bin/activate
pip install -r Brenthy/requirements.txt
pip install walytis_beta_api    # install API library

# run Brenthy, it will offer to install itself
python3 .
```

Brenthy wil ask you whether you want to install or just run it.

For details on how to run Brenthy & Walytis, see [Running From Source](https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Brenthy/User/RunningFromSource.md)

For details on how to install Brenthy & Walytis, see [Installing Brenthy](https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Brenthy/User/InstallingBrenthy.md)

### Use Walytis

1. Install the `walytis_beta_api` Python package:

```sh
pip install walytis_beta_api
```

2. Start playing around in Python:

```python
import walytis_beta_api as waly
blockchain = waly.Blockchain.create("MyFirstBlockchain")
block = blockchain.add_block("Hello there!".encode())
```

Read the [Tutorial](/docs/Tutorials/0-TutorialOverview.md) to learn how to use Walytis, and start building cool stuff!

## Documentation

The above sections already contain some links to relevant parts of Brenthy & Walytis' documentation.
It is still a work in progress, but already covers most aspects.
Dive into the full documentation here: [Documentation Overview](/docs/DocsOverview.md)

## Contributing

### Analysis and Review

If you have any thoughts on Brenthy & Walytis or want to discuss the sensibility of their unique features, feel free to share them under GitHub discussions.
I would especially appreciate reviews and analyses of [Walytis' blockchain-architecture security](/docs/Technical/WalytisBlockchainSecurity.md).

### Software Development

Despite the documentation on Brenthy & Walytis' DevOps not being written yet, feel free to submit pull requests via GitHub if you think you know what you're doing.

### Feature Requests and Bug Reports

If you don't have the time to learn how to contribute code directly, feel free to request features or report bugs via GitHub Issues.

### Documentation Improvement

#TODO
%% GitHub wiki? %%

### Financial Support

To financially support me in my work on this and other projects, you can make donations with the following currencies (more methods coming soon):

- **Bitcoin:** `BC1Q45QEE6YTNGRC5TSZ42ZL3MWV8798ZEF70H2DG0`
- **Ethereum:** `0xA32C3bBC2106C986317f202B3aa8eBc3063323D4`
- [**Fiat** (Credit or Debit Card, Apple Pay, Google Pay, Revolut Pay)](https://checkout.revolut.com/pay/4e4d24de-26cf-4e7d-9e84-ede89ec67f32)

