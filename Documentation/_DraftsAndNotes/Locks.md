Here's a quick overview of the locks used inside of Brenthy to ensure sequential access to certain resources:

# Blockchain.endblocks_lock:
_Blockchain.py_

This lock manages access to the blockchain's list of latest blocks, which is used to get parent blocks when creating blocks and is updated when new blocks are received.

__Used by:__
- Blockchain.CreateBlocks()
- Blockchain.download_and_process_block()
  -> Blockchain.new_block_published()
    -> Blockchain.look_for_blocks_to_find()


# BlockchainAppdata.invitations_lock:
_AppData.py_

This lock manages access to the blockchain's invitation's appdata-file, as invitations are loaded from and saved to appdata or as the appdata file is temporarily modified when sharing it with a newly joining peer.

__Used by:__
- BlockchainAppdata.zip_appdata() 
  -> Blockchain.on_join_request_received()
- BlockchainAppdata.load_invitations()
- BlockchainAppdata.save_invitations()

# BlockRecords.index_lock:
_BlockRecords.py_

This lock manages access to the block-record's index-file, the blockchain's recorded list of all blocks on the blockchain.

__Used by:__
- BlockRecords.check_new_block()
  -> Blockchain.CreateBlocks()
  -> Blockchain.download_and_process_block()
    -> Blockchain.new_block_published()
    -> Blockchain.look_for_blocks_to_find()
  -> BlockRecords.save_block()
    -> Blockchain.download_and_process_block()
    -> Blockchain.new_block_published()
    -> Blockchain.look_for_blocks_to_find()
- BlockRecords.index_file_reader()
  -> BlockRecords.is_block_known()
  -> BlockRecords.count_ids()
  -> BlockRecords.list_ids()
  
