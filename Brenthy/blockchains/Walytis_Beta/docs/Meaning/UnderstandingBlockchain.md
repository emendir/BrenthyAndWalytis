_a basic understanding of what blockchain technologies are and how they work_

## What Blockchains Are

Blockchain is a technology that creates decentralised eternal databases, where users can add new data but not change or delete  existing data.

Its invention was revolutionary in the world of information technology because it provided for the first time a way to guarantee the preservation of data integrity in a dynamic and distributed system.
In plain terms, this means the ability of a person to be sure that a piece of data is original and hasn't been tampered with despite not having received it directly from its author.

It is worth appreciating that this is new not only to digital information technology, but all forms of communication man has ever used, including writing and passing on information by word of mouth.

## How Blockchains Work
A secure and completely decentralised database is a tricky thing to realise.
Blockchain is a technology that achieves this by quantising data into blocks and linking those blocks together cryptographically.
Block chaining consists of blocks encoding within themselves cryptographic hashes of their parent blocks.

_Oversimplified representation of block-chaining in a linear blockchain:_
![](./LinearBlockChaining.drawio.svg)

A block's hash is a small piece of data that is generated from a block's content (data which applications want to store on the blockchain) and other metadata.
If one changes a block's content or metadata, the block's hash changes.

The chaining of blocks generally performs multiple roles:
- By having new blocks reference old blocks, the existence of old blocks can never be forgotten.
- Basic fraudulent manipulation of existing blocks can easily be detected, because the manipulated block would have a different hash than the hash encoded in its children.

A hash being cryptographic means it is hard to cheat the system by figuring out which different block contents and metadata might produce the same hash.
