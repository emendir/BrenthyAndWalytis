# Querying Blocks

The most efficient way to find specific blocks on a Walytis blockchain is to find blocks with specific metadata values.
Of course it's possible to search for blocks based on their content, but since a block's content can be any binary data, this is rather inefficient.
Block metadata, on the other hand, is encoded in the block ID in a specific way, making it much more efficient to query by.


## Homologies with Conventional DBMSs

Let's look at some homologies between conventional database management systems and Walytis when it comes to querying:

| Conventional Databases | Walytis              |
| ---------------------- | -------------------- |
| table                  | blockchain           |
| row                    | block                |
| column/field           | block metadata field |

## Metadata Fields

##### Standard Metadata Fields
Most of a block's metadata fields such as creator, time-stamp etc. exist for technical reasons specific to mechanisms by which Walytis works.

##### Custom Metadata Fields
However, blocks also contain a field called `topics`, which is a list of strings, in which the programmer can store any number of custom pieces of data.
The `topics` field exists specifically to allow the programmer to query their blocks efficiently by labelling or categorising them using the `topics` field.

#### Relevant Block Metadata Fields

These are the block metadata fields you as the user of a Walytis blockchain as a database are most likely to be interested in when querying blocks:

| Field Name       | Data Type       | Description                                                     |
| ---------------- | --------------- | --------------------------------------------------------------- |
| `topics`         | list of strings | user-defined metadata for labelling blocks                      |
| `long_id`        | array of bytes  | the full identifier of a block, encoding all its other metadata |
| `creation_time`  | date-time       | the time at which the block was created                         |
| `creator_id`     | str             | the IPFS peer-ID of the blockchain node that created this block |
| `content_length` | integer         | the size of the block's content in bytes                        |
| `content_hash`   | array of bytes  | a cryptographic hash of the block's content                     |

A complete list of a block's metadata fields is in [Blocks - Block Metadata](/Documentation/Walytis/Technical/Blocks.md#block-metadata).

### Querying Using the Python API

Let's look at how we might query a Walytis blockchain using the `walytis_beta_api` library.

The following example creates a blockchain, adds some blocks to it, and then queries for blocks that meet various conditions.

To perform the actual querying, we using python's list-comprehension together on the `Blockchain` class' `get_blocks()` method.
This provides a syntax familiar to SQL 

```python
from walytis_beta_api import Blockchain, Block
import json
from datetime import datetime

# create a blockchain
bc = Blockchain.create()

# add some blocks to the blockchain
bc.add_block("Hello there, this is Block 1,".encode(), topics=["odd"])
bc.add_block("Hello there, this is Block 2.".encode(), topics=["even"])
bc.add_block(json.dumps({"number": 3}).encode(), topics=["odd", "json"])
timestamp = datetime.utcnow()
bc.add_block(json.dumps({"number": 4}).encode(), topics=["even", "json"])
bc.add_block(json.dumps({"number": 5}).encode(), topics=["odd", "json"])
bc.add_block(json.dumps({"number": 6}).encode(), topics=["even", "json"])

# Run queries

even_blocks:list[Block] = [
    block
    for block in bc.get_blocks()
    if "even" in block.topics
]

new_blocks_times:list[datetime] = [
    block.creation_time
    for block in bc.get_blocks(reverse=True)
    if block.creation_time > timestamp
]

newst_blocks_contents:list[dict] = [
    json.loads(block.content.decode())
    for block in bc.get_blocks()
    if "json" in block.topics and block.creation_time > timestamp
]


bc.terminate() # clean up resources
```

#### Performance

The above example demonstrates the most efficient approach for general querying.

In some cases, performance can be optimised further using an understanding of how the `Blockchain.get_blocks()` method works.

`Blockchain.get_blocks()` is a generator over the hidden `Blockchain._blocks` attribute, which is a dictionary of block-IDs and lazily loaded `Block` objects.
Before any querying is done, `Blockchain._blocks` is nothing more than a list of block IDs: the keys of the dictionary's items a the block-IDs, and the values are `None`.
Whenever an item in this dictionary is accessed, the block metadata is decoded from the block-ID (the item's key) and stored into a `BlockLazilyLoaded` object as the value of the item.
Accessing an item for the first time costs time, but accessing it again afterwards is much faster.
The `BlockLazilyLoaded` has exactly the same fields as the `Block` class, which it inherits.
However, its fields are lazily loaded, meaning the block metadata only get decoded from the block ID the first time they are accessed.
The block content, which takes even more processing power and time to load than the metadata, is also loaded only when it is first accessed.
Again the first access costs time, but also increased memory use.

To study these effects more closely, read and run this python script:
[block_lazy_loading_demo.py](/Documentation/Walytis/Technical/block_lazy_loading_demo.py)

Warning: Don't use `Blockchain._blocks` directly in your code, because I don't guarantee I won't change it's behaviour without warning, wherefore it is hidden. Use the methods described in the next section instead. 
#### Other Block Functions

In implementing these gains in querying performance, a few ergonomic compromises were made.
For example, because `Blockchain.get_blocks()` returns a generator instead of a normal list, one can't simply call `len(Blockchain.get_blocks())` to get the number of blocks in the blockchain.
To compensate this lack of ergonomics, the `Blockchain` class has the the following methods for accessing various aspects of blocks:

| Method Name    | Parameters              | Return            | Description                                                                  |
| -------------- | ----------------------- | ----------------- | ---------------------------------------------------------------------------- |
| `get_blocks`   | `reverse: bool = False` | `Iterable[Block]` | allows user to iterate over all blocks, accessing their metadata and content |
| get_block_ids  |                         | `list[bytes]`     | get a list of all block IDs                                                  |
| get_num_blocks |                         | `int`             | get the number of blocks in the blockchain                                   |
| `get_block`    | `id: bytes`             | `Block`           | get a `Block` object given its block ID                                      |

