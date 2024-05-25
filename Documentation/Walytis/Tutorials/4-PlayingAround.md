# Playing Around

Now that you know how to build applications that use Walytis blockchains, let's look at some tools which `walytis_beta_api` provides to help in the development process.

## REPL Interaction

If you want to check on the status of your blockchain in a python console (REPL) or using something like Jupyter, it could be impractical to find the blockchain you're interested in by looking at the available blockchains' IDs.
Therefore, `walytis_beta_api` allows you to specify a local name for blockchains to make it easier to identify and specify them when using interactive Python consoles.
Note that the blockchain names are only valid in the scope of your local computer: you might create a blockchain named "FamilyPhotos", and so might your neighbour, resulting in two different blockchains with the same local names. 
If you shared your "FamilyPhotos" blockchain with your friend, they might call it "FamilyAndFriendsPhotos" on their computer, to distinguish it from their own "FamilyPhotos" blockchain.
For this reason it is important that you do not use blockchain names to specify and identify them in applications, only when manually interacting with them in Python consoles.

### Using Blockchain Names

1. Start by creating a blockchain, and specify a name for it in the process:
```python
import walytis_beta_api
walytis_beta_api.create_blockchain(blockchain_name="NamedBlockchain")
```
2. When we list the available blockchains, we see the IDs and names of the blockchains:
```python
walytis_beta_api.list_blockchains()
```
We can a list of only the blockchain names, we use the `list_blockchain_names` function:
```python
walytis_beta_api.list_blockchain_names()
```
3. We can instantiate a Blockchain object using the name:
```python
blockchain = walytis_beta_api.Blockchain("NamedBlockchain")
```
4. Most other blockchain-related functions will accept a blockchain name in the place of a blockchain ID. Here's us cleaning up after this demonstration:
```python
blockchain.terminate()
walytis_beta_api.delete_blockchain("NamedBlockchain")
```

### Quickly Accessing Blocks

If you want to check the content or other properties of the latest block created, you can do that quite easily with a single line:
```python
blockchain.get_block(-1).content
```
Blockchain.get_block() was originally built to take a block ID as input, but its functionality was extended to take the index of the block ID in the list of known and already processed blocks. `blockchain.get_block(-1)` is essentially a shortcut for `blockchain.get_block(blockchain.block_ids[-1])`

