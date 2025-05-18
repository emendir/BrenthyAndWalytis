_the version numbering systems of Walytis, the Walytis Protocol, the Walytis API, and the `walytis_api` library_

Some of the different components of Walytis have their own version numbers, which are partially interdependent.
The Walytis Node and `walytis_api` version numbering follows the standard three-part major-minor-patch model, and are composed of the version numbers of the Walytis Protocol and the WalytisAPI protocol.
Here are explanations for how exactly these relationships work, and what exactly version number jumps in these different components mean in terms of development.

## Walytis Protocol Versioning
_The Walytis protocol encompasses the mechanisms by which Walytis nodes intercommunicate and how block IDs and block-files are structured._

The Walytis protocol version is represented by a single number which is incremented with every update that changes any of the following:
- the way Walytis nodes communicate with each other
- the structure of the block-file
- the structure of the block-ID

## WalytisAPI Protocol Versioning
_The WalytisAPI protocol defines how Walytis nodes and the `walytis_api` library communicate with each other._

The WalytisAPI protocol version is represented by two numbers, the first of which is the Walytis protocol version.
The second number is incremented with every update that changes the way the Walytis node software and the Walytis-API library communicate with each other.

## Walytis Core Versioning
_Walytis Core refers to the actual software manifesting a Walytis node, running blockchains, communicating with other nodes, interacting with applications etc._

The Walytis Core version consists of three numbers: major, minor and patch.
- The major version is the most recent Walytis protocol version.
- The minor version and major versions together make up the most recent Walytis API protocol version.
- The patch version is incremented with every update to the Walytis node that does not interfere with the Walytis protocol or the Walytis API protocol.

## `walytis_api` Library Versioning
The `walytis_api` version consists of three numbers: major, minor and patch.
- The major version is the most recent Walytis protocol version.
- The minor version and major versions together make up the most recent Walytis API protocol version.
- The patch version is incremented with every update to the `walytis_api` library that does not interfere with the Walytis protocol or the Walytis API protocol.
