## API
- class Blockchain: By default, add newly received block to block_ids before or after running user's event handler?
- class Block: use bytes instead of bytearray?
- topics: `set[bytearray|bytes]` instead of `list[str]`
- topics: rename to user-metadata? What about non-user metadata ("Genesis", blockchain-ID)? Maybe separate into topics and user-metadata, which is simply a subset of the former 
- more efficient block lookup, perhaps tell walytis_beta_api to read the blocks' folder?
- Walytis: get rid of DBMS?