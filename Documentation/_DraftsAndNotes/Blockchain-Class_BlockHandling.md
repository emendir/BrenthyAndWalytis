

### current_endblocks:
list(bytearray)

A list for storing the short block_ids newest known blocks for use as parent-blocks when creating new blocks.

Ideal size: min_num_parentblocks

Blocks are added on startup (latest blocks from appdata), when a new block is received or created.  
Blocks are removed when a new block is created and the list has more than enough blocks.

### unconfirmed_blocks:
list(Block)

A list of blocks that have been received but whose parent blocks haven't all been found.

Blocks can be added when a block is received.
Blocks can be removed when a block from the blocks_to_find list gets received.

### blocks_to_find:
list(bytearray)

A list of short_ids of blocks that we have heard of from the parent-blocks list of received block, but haven't yet received.

Block_ids are added when a block is received and unconfirmed and added to unconfirmed_blocks.
Block_ids are be removed when their blocks are received.