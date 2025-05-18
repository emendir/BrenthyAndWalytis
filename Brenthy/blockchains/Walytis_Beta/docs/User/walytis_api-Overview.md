_an overview of the functions and classes in the `walytis_api` library_

_For more detailed information about the API's functions and classes, see the [API-Reference](../API-Reference/walytis_beta_api/walytis_beta_interface.html)_.
_For a more user-friendly guide on how to use the API, see the [the walytis_api tutorials](../Tutorials/0-TutorialOverview.md) ._
_To learn how WalytisAPI works to connect applications with blockchains, see [WalytisAPI](/docs/Technical/WalytisAPI.md)_.

`walytis_api`, the Walytis Application Programming Interface, is a programming library that allows programmers to create, manage and interact with Walytis blockchains.
Programmers import and use it in their code, as in the following example:
```python
import walytis_api

blockchain = walytis_api.Blockchain.create() # create a blockchain
blockchain.add_block("Hello there!".encode()) # put data on the blockchain
```

Use [the tutorials](../Tutorials/0-TutorialOverview.md) to learn how to use the Walytis API library.
See the [API reference](../API-Reference/walytis_beta_api/index.html) for detailed list of all the functions and classes it contains, explaining what they do and how to use them.
This page provides a well-structured overview of `walytis_api`'s main functionality.

## Library Overview

### Functional and Object-Oriented Usage
`walytis_api` provides functions and classes for interacting with and managing Walytis blockchains.
While the programmer can achieve all functionality using a purely functional programming approach, an object-oriented approach is strongly recommended as the `Blockchain` class includes machinery for keeping track of which applications have been notified of which new blocks, which the programmer would have to replicate themselves if they used a purely functional approach.

### Functions

API reference: [../API-Reference/walytis_beta_api/walytis_beta_interface.html](../API-Reference/walytis_beta_api/walytis_beta_interface.html) 
#### Managing Blockchains

Here is a summary (not a complete list) of the main blockchain-management functions provided by `walytis_api`:
- list_blockchains
- create_blockchain
- join_blockchain
- delete_blockchain

#### Interacting with Blockchains

Here is a summary (not a complete list) of the main functions for interacting with blockchains.
All of these functions operate on an instance of a blockchain, whose blockchain ID they take as their first parameter.
- create_block
- get_block
- is_block_known
- get_latest_blocks
- create_invitation
- get_invitations
- delete_invitation


### Classes

#### `class Blockchain`

API reference: [../API-Reference/walytis_beta_api/blockchain_model.html](../API-Reference/walytis_beta_api/blockchain_model.html) 

The `Blockchain` class isn't the code running the Walytis blockchains themselves, it is merely a construct of `walytis_api` for representing a blockchain.
It does more than just bundling the functions listed under _Interacting with Blockchains_ into a class:
It has mechanisms for keeping track of individual applications' notification of new blocks, notifying them when they come online after a period of sleep which blocks have been received in the meantime, as well as ensuring they are notified of new blocks in the correct order.

Here is a summary (not a complete list) of the main methods the `Blockchain` class provides:
- add_block
- get_block
- create_invitation
- delete_invitation
- get_invitations

It also has the field `block_received_handler`, which the user can set to a function they define to be called when a new block is received.
##### Managing Blockchains

Here is a summary (not a complete list) of the blockchain-management methods the `Blockchain` class provides:

- create (static method)
- join (static method)
- delete
 
#### `class Block`
API reference: [../API-Reference/walytis_beta_api/block_model.html](../API-Reference/walytis_beta_api/block_model.html#walytis_beta_api.block_model.Block) 

While the `block` class in `walytis_api` provides access to all a block's low-level properties, and even provides the blockchain-context-independent block-integrity-verification functions, most programmers will only use the following attributes of the `block` class:
- content
- topics

The `content` field contains the data which the application that created the block chose to store in it.
`topics` is a list of labels that applications can add to a block to allow for quick filtering of blocks without analysing their content.
