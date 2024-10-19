## API
- class Blockchain:
  - By default, add newly received block to block_ids before or after running user's event handler?
  - parameter `update_blockids_before_handling`: rename to `update_blocks_before_handling`
- class Block: use bytes instead of bytearray?
- topics: elements of type `bytearray|bytes` instead of `str`
- topics: collection of type `set` instead of `list`? `set`s aren't sorted...
- topics: rename to user-metadata? What about non-user metadata ("Genesis", blockchain-ID)? Maybe separate into topics and user-metadata, which is simply a subset of the former 
- more efficient block lookup, perhaps tell walytis_beta_api to read the blocks' folder?
- Walytis: get rid of DBMS?
- class Blockchain: don't provide block info after object is terminated



## General
- remove all code marked with comments of BACKWARDS COMPATIBILITY