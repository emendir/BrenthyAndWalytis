## Block Data-File Structure:
_Note that it doesn't explicitly contain the block ID_

blockchain version  
00  
block creator's short_id  
00  
block creation time  
00  
topic1  
0  
topic2  
0  
...   
...   
topicx
00
block content length  
00  
hash algorithm name
00
hash
00
n_parents
00
parents_hash_algorithm
00
parents_hash
0000  
parent1 short_id          (standard ID format (see below))  
000  
parent2 short_id          (standard ID format (see below))  
000  
...  
...  
parentx short_id
00000

content             (array of bytes)  
0

hash                (array of bytes that don't contain 0)  

## ID Structures:
### Short Block ID structure:
blockchain_version + 00 + ipfs_cid + 00 + creator_id + 00 + timestamp + 00 + topic1 + 0 + topic2 + 0 + ... topic_n + 00 + content_length + 00 + content_hash_algorithm + 00 + self.hash + n_parents + 00 + parents_hash_algorithm + 00 + parents_hash
### Long Block ID structure:
short_block_id + 0000 + parent1 + 000 + parent2 + 000 + ... + parent_n

All bytearrays between the 0s do not include 0s. The numbers representing the creation datetime are encoded into base 255 numbers where each digit is stored in a single byte and has a value between 1-255.
The zeroes act as separators so that the short_id can be read with no rules about the length of each component bytearray, allowing for an infinite range of IDs.

## Ancestry Traced code:
1: True  
2: False  
3: haven't checked yet
