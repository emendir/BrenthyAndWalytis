![](/Graphics/BrenthyIcon.png)

# Brenthy & Walytis

_`4D61646520776974682073696E63657265206C6F766520666F72206D616E6B696E642E`_

Brenthy & Walytis are technologies that take the development of blockchain tech to a new level.
Walytis is a lightweight, flexible, accessible and application-oriented type of blockchain, and Brenthy is a framework to aid the development and deployment of new blockchain types.

Developed together, they share a repository because they rely on each other very strongly.

## [Walytis](Documentation/Walytis/Meaning/IntroductionToWalytis.md)

_A flexible, lightweight, nonlinear blockchain, built to be built upon._

Walytis is a type of blockchain that is essentially a fully distributed database-management system with a focus on accessibility, flexibility and lightweightedness.
Applications can create a new Walytis blockchain (i.e. a new database) whenever they need one.
While they can always add new data to it, existing data can never be deleted or modified.

Learn about Walytis here: [Introduction to Walytis](/Documentation/Walytis/Meaning/IntroductionToWalytis.md)  
Learn why Walytis was developed: [Walytis' Rationale](/Documentation/Walytis/Meaning/WalytisRationale.md)  
Walytis project source: [./Brenthy/blockchains/Walytis_Beta](/Brenthy/blockchains/Walytis_Beta/ReadMe.md)

## [Brenthy](/Documentation/Brenthy/Meaning/IntroductionToBrenthy.md)

_A framework for developing and deploying new kinds of blockchains._

Brenthy takes care of all the non-blockchain-related machinery like installation, update and auto-start of itself and its blockchain types.
It also provides API-infrastructure to ease the development of blockchain APIs for applications.
Using these ready-made features of Brenthy's allows developers of new blockchains to focus on developing their blockchain's core.

Learn about Brenthy here: [Introduction to Brenthy](/Documentation/Brenthy/Meaning/IntroductionToBrenthy.md)  
Brenthy project source: [./Brenthy](/Brenthy/ReadMe.md)

### What makes Walytis special to Brenthy:

- Brenthy uses Walytis: A Walytis blockchain lies at the core of Brenthy's update system.
- Developed together: Brenthy & Walytis were developed as one project, and were compartmentalised to facilitate other blockchain inventors in developing and deploying their inventions.
- Live in the same repository: The code for Brenthy & Walytis live in the same repository to ease their development, testing, installation & deployment.

## Getting Started

### Install or Run from Source

Ubuntu quick start:

```sh
# install prerequisites
sudo apt update && sudo apt install -y python3-virtualenv git

# download BrenthyAndWalytis
git clone https://github.com/emendir/BrenthyAndWalytis
cd BrenthyAndWalytis

# install the Walytis blockchain
Brenthy/blockchains/install_walytis_beta.sh

# set up python environment (you can skip this if you only want to install)
virtualenv .venv && source .venv/bin/activate
pip install -r Brenthy/requirements.txt
pip install walytis_beta_api    # install API library

# run Brenthy, it will offer to install itself
python3 .
```

Brenthy wil ask you whether you want to install or run it from source.

For details on how to run Brenthy & Walytis, see [Running From Source](/Documentation/Brenthy/User/RunningFromSource.md)

For details on how to install Brenthy & Walytis, see [Installing Brenthy](/Documentation/Brenthy/User/InstallingBrenthy.md)

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

Read the [Tutorial](/Documentation/Walytis/Tutorials/0-TutorialOverview.md) to learn how to use Walytis, and start building cool stuff!

## Documentation

The above sections already contain some links to relevant parts of Brenthy & Walytis' documentation.
It is still a work in progress, but already covers most aspects.
Dive into the full documentation here: [Documentation Overview](/Documentation/DocsOverview.md)

## Contributing

### Analysis and Review

If you have any thoughts on Brenthy & Walytis or want to discuss the sensibility of their unique features, feel free to share them under GitHub discussions.
I would especially appreciate reviews and analyses of [Walytis' blockchain-architecture security](/Documentation/Walytis/Technical/WalytisBlockchainSecurity.md).

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

