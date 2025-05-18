## Preparing to Start

### Install Prerequisites
- **Brenthy & Walytis:** First of all, you'll need Brenthy & Walytis installed. Brenthy is a program that runs in the background on your computer as a service, which runs the software of various blockchain types, such as the Walytis software which runs Walytis blockchains. Follow [these instructions](https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Brenthy/User/InstallingBrenthy.md) for installing them.
- **`walytis_beta_api`:** To interact with Walytis, you'll need the `walytis_beta_api` Python library installed. See [Installing walytis_api](../User/Installing-walytis_api.md).
- **Python3:** If you need help with this, visit its homepage at https://python.org to get started.

To test that everything is working, run the following shell command:
```shell
python -c "import walytis_beta_api;print(walytis_beta_api.get_walytis_beta_version_string())"
```
The command should return a version number, such as `0.1.5`

## Interacting With Walytis in Python

With the prerequisites installed, you can start interacting with Walytis in Python.

First of all, import the `walytis_beta_api` module, which provides all the machinery you need to interact with Walytis:
```python
import walytis_beta_api
```

### First Steps With Walytis

The simplest way to create a blockchain is with the following code:
```python
blockchain_id = walytis_beta_api.create_blockchain()
```
Great! How do we test it and add a block? How do we handle the event of a new block being added to the blockchain?

First, let's create a function to handle receiving blocks:
```python
def on_block_received(block):
    print("Received a new block!")
    print(block.content)
```

Then, let's get a `Blockchain` object to represent our newly created blockchain:
```python
my_blockchain = walytis_beta_api.Blockchain(
    blockchain_id=blockchain_id,
    block_received_handler=on_block_received
)
```

Here, we ask `walytis_beta_api` for a `Blockchain` object representing the blockchain we just created. 
- `blockchain_id` lets `walytis_beta_api` know which blockchain we want.
- `block_received_handler` tells `walytis_beta_api` which function to call when a new block is added to the blockchain.

Now let's create a block with a simple piece of text as content.
Block content is is of type `bytearray`, so we'll have to convert our text into bytes before we pass it to the `add_block` function:
```python
first_block = my_blockchain.add_block("Hello there!".encode())
```

Now, you might be wondering, Shouldn't the `on_block_received` function execute now and print the block's content?
Well, that function only executes when receiving blocks which we didn't create ourselves, so it won't execute here.
We'll see it coming into action later on when we interact with the blockchain from multiple computers.
But you can see the block is on the blockchain by checking the content of the blockchain's newest block:
```python
print(my_blockchain.get_block(-1).content) # -1 means the last block
```

For now, let's explore a bit with what we have, taking a look at some of the attributes of the `Blockchain` and `Block` classes:
```python
print(first_block.content)
print(first_block.creation_time)
print(first_block.creator_id) # creator ID looks a bit like an IPFS peer ID, doesn't it? It is one!
import ipfs_api
print(ipfs_api.my_id()) # my creator ID is the same as my IPFS ID!

print(first_block.parents)
for i, block_id in enumerate(my_blockchain.block_ids):
	print(i, block_id)
```

After checking out your first block's parents attribute, you found out that you already have 5 blocks older than it, giving you a total of 6 blocks on the blockchain now! 
That's because when creating a blockchain, 5 genesis blocks are created to start the blockchain off.
```python
genesis_block = my_blockchain.get_block(0)
print(genesis_block.parents) # genesis block has no parents
print(genesis_block.short_id)
print(genesis_block.ipfs_cid)
print(genesis_block.ipfs_cid == my_blockchain.id)

print(genesis_block.topics)
print(first_block.topics)
```

Here you've discovered block topics. The automatically created genesis blocks have 'genesis' as a topic, the ones you create have the blockchain ID as a topic, which is incidentally the same as the genesis block's (or the first of the five genesis blocks') IPFS content ID!

You can add topics to blocks yourself, they're there for you to use:
```python
second_block = my_blockchain.add_block("Hello again!".encode(), topics=["just-playing-around", "tutorial"])
print(second_block.topics)
print(second_block.short_id)
```

When looking at a block ID, you can see the topics encoded in it.
That's the purpose of block topics:  They are a piece of user-definable metadata that isn't encoded in the block content, but instead in the block-ID.
This makes it possible to read that metadata efficiently by just looking at the block's ID without opening the block-file and decoding the block content first.

#### Cleaning Up

You'll probably notice that if you've been trying out the above code in a Python console (REPL), when you use `exit()` or Ctrl+D, you have to follow it with Ctrl+C to exit properly.
This is because the `Blockchain` object runs another thread with open connections to the core Walytis software running in Brenthy to get notifications of new blocks, so when you tell the Python console to close, it doesn't do so because there is still some code running in the background.
To close these connections and clean up the resources being used, call the following line at the end of your code before exiting:
```python
my_blockchain.terminate()
```
