## API
### class Blockchain:
  - By default, add newly received block to block_ids before or after running user's event handler?
  - parameter `update_blockids_before_handling`: rename to `update_blocks_before_handling`
  - rename `get_block_ids()` to `block_ids`
  - rename `get_blocks()` to `blocks`
  - don't provide block info after object is terminated
  - better name for `load_missed_blocks`, such as `start_receiving_blocks`
    - if `False`, don't process any incoming blocks

### class Block:
  - use bytes instead of bytearray?
  - rename `long_id` to `id`
  - rename `short_id` to `childrens_reference` or similar
    - topics: elements of type `bytearray|bytes` instead of `str`
    - topics: collection of type `set` instead of `list`? `set`s aren't sorted...
    - topics: rename to user-metadata? What about non-user metadata ("Genesis", blockchain-ID)? Maybe separate into topics and user-metadata, which is simply a subset of the former 
- more efficient block lookup, perhaps tell walytis_beta_api to read the blocks' folder?
- Walytis: get rid of DBMS?

- migrate from `datetime.utcnow()` to datetime.now(UTC)
- `join_blockchain_from_zip`: is `blockchain_id` parameter redundant?


## General
- remove all code marked with comments of BACKWARDS COMPATIBILITY

- Blockchain ID: Make it more verifiable - the IPFS CID of the last geneis Block?