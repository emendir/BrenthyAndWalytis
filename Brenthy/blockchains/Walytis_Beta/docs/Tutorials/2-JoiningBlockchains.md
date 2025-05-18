# Joining Blockchains

Now that you know how to create a Walytis blockchain, create blocks and play around with some of their attributes, it's time to learn how to interact with blockchains from multiple computers.
In this section we will look at how to get multiple computers to interact with the same blockchain.

## New Prerequisites

You will need a second computer (physical or virtual machine) with Brenthy & Walytis, Python and `walytis_beta_api` installed. It should either be in the same LAN as your primary computer or they should both have internet access.

Make sure the two computers can communicate with each other.
You can test this by using IPFS pings, using the IPFS command-line utility, which should have been installed by the Brenthy installer.
- On each computer, run the `ipfs id` command in a terminal to get that computer's IPFS peer ID
```shell
ipfs id
```
- Then, on each computer run the `ipfs ping` command followed by the IPFS peer ID of the other computer, testing whether they each can communicate with the other computer via IPFS:
```shell
# replace PEER_ID with the output of the `ipfs id` command on the other computer
ipfs ping PEER_ID
```
- If the computers can communicate with each other, you will see new lines of output appearing in the console at regular time intervals, somewhat like the following:
```
Pong received: time=1.26 ms
Pong received: time=0.50 ms
Pong received: time=0.82 ms
``` 
- Otherwise you'll need to troubleshoot your computers' networking until they can communicate.

## Joining Blockchains in Python

To allow computer B to interact with the blockchain you created on computer A, we'll create an invitation code which computer B can use to join your blockchain.

Computer A:
```python
import walytis_beta_api

blockchain_id = "PUT_YOUR_BLOCKCHAIN_ID_HERE"

def on_block_received(block):
    print("Received a new block!")
    print(block.content)

my_blockchain = walytis_beta_api.Blockchain(
    blockchain_id=blockchain_id,
    block_received_handler=on_block_received
)
invitation_code = my_blockchain.create_invitation(one_time=False)

print(invitation_code) # copy the output of this command
```

The `one_time` parameter determines whether the invitation you create should only be valid once or reusable.

Now that you have the invitation code, switch to the other computer and use the code to join your blockchain there.  
Computer B:
```python
import walytis_beta_api

invitation_code = 'PUT_YOUR_INVITATION_CODE_HERE'
blockchain_id = walytis_beta_api.join_blockchain(invitation_code)
```

In the joining process, the Walytis program running on Computer B communicates to the Walytis program running on Computer A (Computer A's IPFS peer ID is encoded in the invitation). After verifying the validity of the invitation code, Computer A sends all of its blockchain data to computer B.

Let's see if we got the blockchain:

Computer B:
```python
print(walytis_beta_api.list_blockchain_ids())
```

You'll see that you have two blockchains: one is called `BrenthyUpdates`, which comes preinstalled by Brenthy to manage its own updates, and the second is the one that you created on computer A.

Let's check it out:

Computer B:
```python
def on_block_received(block):
    print("Received a new block!")
    print(block.content)

my_blockchain = walytis_beta_api.Blockchain(
    blockchain_id=blockchain_id,
    block_received_handler=on_block_received
)
```

When running this code, you'll see that the `on_block_received` becomes active, running for every block you created on computer A.

Create a block on computer B:

Computer B:
```python
my_blockchain.add_block("Hi back!".encode())
```

You should see the `on_block_received` eventhandler run on computer A.
