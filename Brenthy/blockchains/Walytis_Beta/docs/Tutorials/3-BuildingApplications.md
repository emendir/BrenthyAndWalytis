## Building Applications

At this point you know all the essentials of how to work with Walytis blockchains.
When it comes to building an application that uses a Walytis blockchain, `walytis_beta_api` has a bit of extra built-in machinery to help you on your way.
In this section we will look into some of the basic challenges that arise when building an application that uses a blockchain, and how to use `walytis_beta_api`'s features for handling them.

## Making Efficient Use of `walytis_api` in Python

### Keeping Track of Processed Blocks

##### Step 1

Run the following bit of code.
It's nothing new, copied and pasted from the last section of this tutorial, and it cleans up and exits immediately after creating the blockchain object.
```python
import walytis_beta_api

def on_block_received(block):
	"""Eventhandler to be called whenever a new block is received"""
	print("Received a new block!")
	print(block.content)

# create a Blockchain object to represent the blockchain we created earlier
blockchain_id = walytis_beta_api.list_blockchain_ids()[-1]
my_blockchain = walytis_beta_api.Blockchain(
	blockchain_id=blockchain_id,
	block_received_handler=on_block_received
)

# clean up the Blockchain object
my_blockchain.terminate()
exit() # if you're in a python console (REPL), exit
```

Now, run it again.
If you're working in an interactive Python console such as in the terminal or Jupyter notebook, open a new console that is independent of the first, because we need to simulate an app running for a second time after it was closed.
Each time you run this code, the `on_block_received` function gets called for every block ever created on that blockchain (except for the automatically generated genesis blocks).
You probably want your application to only ever process each block once, regardless of how often your app restarts.

So somehow you need to keep track of which blocks you've processed, so that you can ensure that you only ever process blocks that are new to you.
`walytis_beta_api` already has the machinery to do that for you, and using that is very easy.

##### Step 2

Let's modify the above code by adding only a single new parameter to the blockchain's constructor:
```python
import walytis_beta_api


def on_block_received(block):
	"""Eventhandler to be called whenever a new block is received"""
	print("Received a new block!")
	print(block.content)

# create a Blockchain object to represent the blockchain we created earlier
blockchain_id = walytis_beta_api.list_blockchain_ids()[-1]
my_blockchain = walytis_beta_api.Blockchain(
	blockchain_id=blockchain_id,
	app_name="Tutorial",
	block_received_handler=on_block_received
)

# clean up the Blockchain object
my_blockchain.terminate()
exit() # if you're in a python console (REPL), exit
```
  
  The `app_name` parameter allows `walytis_beta_api` to keep track of which blocks it has run the block-received eventhandler for, for our app.
  When running this code a second time, the `on_block_received` won't get triggered any more.
  Change `app_name` to a different string, and the eventhandler will be executed again, but only for the first time you ever run that code, because every time you run it afterwards, `walytis_beta_api` will recognise your app and remember that it has already notified your app about those blocks.

##### Step 3

Close your app, and create a block as an anonymous app:
```python
import walytis_beta_api

# create a Blockchain object to represent the blockchain we created earlier
blockchain_id = walytis_beta_api.list_blockchain_ids()[-1]
my_blockchain = walytis_beta_api.Blockchain(blockchain_id)

my_blockchain.add_block("This block is from step 3.".encode())

# clean up the Blockchain object
my_blockchain.terminate()
exit() # if you're in a python console (REPL), exit
```
##### Step 4

Now, run your app again (the code from step 2).
The block-received eventhandler runs once for the block created in step 3, because `walytis_beta_api` remembers that it hasn't given your app that block yet, but has given you all blocks before it.

##### Step 5

Close your app, and create two blocks as an anonymous app:
```python
import walytis_beta_api

# create a Blockchain object to represent the blockchain we created earlier
blockchain_id = walytis_beta_api.list_blockchain_ids()[-1]
my_blockchain = walytis_beta_api.Blockchain(blockchain_id)

my_blockchain.add_block("This is the first block from step 5.".encode())
my_blockchain.add_block("This is the second block from step 5.".encode())

# clean up the Blockchain object
my_blockchain.terminate()
exit() # if you're in a python console (REPL), exit
```

##### Step 6

Now, run your app again (the code from step 2).
The block-received eventhandler runs first for the first block created in step 5, then again for the second.
`walytis_beta_api`always gives your app the blocks it missed in chronological order, the order in which the Walytis service running in the background on your computer processed them, to be precise.

#### `walytis_api`'s Application-Block-Processing Tracking

To summarise, here is a complete list of what `walytis_api` can do to keep track of your app's processed blocks:
- Passing a value for the `app_name` parameter when creating a `Blockchain` object with `walytis_beta_api` makes `walytis_beta_api` keep track of which blocks it triggers your provided block-received eventhandler for, to make sure that it only triggers your app's eventhandler once for every block.
- When your app starts after having been offline for a while, `walytis_beta_api` triggers the eventhandler of all the blocks received by Walytis running in the background while your app was not running.
- It passes those blocks to your app in the same order which your computer's Walytis node processed them in. While the `creation_time` of a later block may be earlier than that of an earlier block, a parent block is guaranteed to be processed before any of its child blocks.
- If your block-received eventhandler raises an exception, `walytis_beta_api` will try to run it again for the same block until it succeeds in running your eventhandler without error before running it for the next blocks.
