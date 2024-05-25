_the API infrastructure Brenthy provides to blockchain types_
_To learn how BrenthyAPI is used by WalytisAPI to allow applications to interact with Walytis, see [WalytisAPI](WalytisAPI.md)_.

# BrenthyAPI

BrenthyAPI is the infrastructure (coded in `api_terminal` and `brenthy_api`) which Brenthy provides to blockchain types to allow them to communicate with their API libraries.
The `brenthy_api` module of the `brenthy_tools` library (upon which blockchain APIs such as `walytis_api` are built) communicates with `api_terminal`, a module of the core Brenthy software.

`brenthy_tools` is a package that contains utilities common to both its `brenthy_api` sub-package and Brenthy's core software. 
You can install the `brenthy_tools` python library and use `brenthy_api` to do some very basic interaction with the installed Brenthy instance yourself, such as looking up Brenthy's version.

Here's some Python code for that. Brenthy needs to be running for it to work.
```python
from brenthy_tools import brenthy_api
print(brenthy_api.get_brenthy_version())
```

## Blockchain APIs

### Application Requests
In the above code example in which we looked up Brenthy's version, we used `brenthy_api` to make a request to Brenthy itself.
BrenthyAPI's main purpose however is to forward requests and responses between a blockchain's API library (used by applications) and the blockchains running in Brenthy.

When sending a request from a blockchain's API library to Brenthy, `brenthy_api` encodes the blockchain library's blockchain type into the BrenthyAPI requests so that Brenthy's `api_terminal` knows which blockchain to forward the request to.

Here's that encoding being done in `brenthy_api`'s `send_request` function:
```python
# from Brenthy/brenthy_tools_beta/brenthy_api.py

def send_request(blockchain_type: str, payload: bytearray | bytes) -> bytearray:
	request = blockchain_type.encode() + bytearray([0]) + payload
```


Let's have a look at how a blockchain API library might use `brenthy_api.send_request`.
Here's the `_send_request` function from the Walytis blockchain's `walytis_api` library:
```python
# from Brenthy/blockchains/Walytis_Beta/walytis_beta_api/walytis_beta_interface.py

def _send_request(function_name: str, payload: bytearray):
	# compose request to Walytis, encoding the library's version, remote function to call, and payload
	request = (
		encode_version(WALYTIS_BETA_API_PROTOCOL_VERSION)
	    + bytearray([0]) + function_name.encode()
	    + bytearray([0]) + payload
	)
	
	# use brenthy_api to send this request to Walytis
	reply = brenthy_api.send_request("Walytis_Beta", request)
```

`brenthy_api` sends requests in binary.
This gives the blockchain full flexibility in the encoding it wants to use, e.g. plain packet-size efficient binary like Walytis does, JSON, or XML.

When communicating to Brenthy itself instead of one of its blockchains, "Brenthy" is encoded into the message in the place of the blockchain type.
Here's that being done in `brenthy_api`'s `send_brenthy_request` function:
```python
# from Brenthy/brenthy_tools_beta/brenthy_api.py

def send_brenthy_request(function_name: str, payload: bytearray):
	request = function_name.encode() + bytearray([0]) + payload
	return send_request("Brenthy", request)
```

In summary, each BrenthyAPI message is tagged with a blockchain type or with "Brenthy", so that Brenthy's `api_terminal`, the module which receives BrenthyAPI requests, knows whom to pass the requests on to.
We can see this decision making coded in the `request_router` function in Brenthy's `api_terminal` module:
```python
# from Brenthy/api_terminal/api_terminal.py

def request_router(request: bytearray):
	# extract the blockchain type and payload from the request
	blockchain_type = request[: request.index(bytearray([0]))].decode()
	payload = request[request.index(bytearray([0])) + 1:]

	# handle Brenthy requests
	if blockchain_type == "Brenthy":
	    return bytearray([1]) + brenthy_request_handler(payload)

	# look for the destination blockchain, forward the request to it
	for blockchain_module in blockchain_manager.blockchain_modules:
	    if blockchain_module.blockchain_type == blockchain_type:

			# ask the blockchain to process the request
	        reply = blockchain_module.api_request_handler(payload)

			# return response or error message, to be sent back to brenthy_api
	        if reply:
				# bytearray([1]) means success
				return bytearray([1]) + reply
			else:
		# bytearray([0]) signals failure
		return bytearray([0]) + json.dumps(
			{'error': BLOCKCHAIN_RETURNED_NO_RESPONSE}
		)
```

Now we've seen how with BrenthyAPI requests, applications can perform Blockchain operations (RPCs - Remote Procedure Calls), or simply ask for a certain piece of information.
In both cases the requestee (the blockchain or Brenthy) responds with a reply: a report on whether the operation succeeded in the case of the RPC, or with the requested information in the latter case.


### Blockchain Publications

When using BrenthyAPI requests, the application decides when an operation should be performed or when it wants to get a piece of information.
When things happen on the blockchain that are outside the application's control, it is the blockchain running in Brenthy that must initiate the communication to inform the application of the event in a timely fashion.

To do this, BrenthyAPI uses a publish-subscribe system (pubsub for short).
On Brenthy's side, the `api_terminal` takes the role of publisher and creates a pubsub socket.
On the blockchain API library's side, `brenthy_api` is used to subscribe to that socket.
On Brenthy's side, a blockchain can publish a message on the pubsub socket and it will be received by any application that has subscribed to it.

The blockchain also specifies so-called topics in the messages, by which the subscribers can filter.
This allows the same publishing socket to be used for different types of messages, while the subscribers can configure their subscribing sockets to only receive messages published under topics relevant to their functionality.

Let's look at how the Walytis blockchain publishes messages about new blocks being received by the `Blockchain` object in `walytis_api`:

In `walytis.Blockchain.download_and_process_block()`:
```python
# from Brenthy/blockchains/Walytis_Beta/walytis_beta.py

# inform applications about the new block
walytis_beta_api_terminal.publish_event(
	self.id,
	message={'block_id': bytes_to_string(block.short_id)},
	topics="NewBlocks",
)
```
`download_and_process_block` passes the event message and topics to `walytis_beta_api_terminal.publish_event` along with its blockchain ID.
`walytis_beta_api_terminal.publish_event` encodes the blockchain ID into the topic, before passing on the event to `api_terminal.publish_event`, along with its blockchain type:

```python
# from Brenthy/blockchains/Walytis_Beta/walytis_beta_api_terminal.py
def publish_event(
	...
	):
	...
	api_terminal.publish_event(
        "Walytis_Beta",
        message,
        topics=[f"{blockchain_id}-{topic}" for topic in topics]
    )
```

In `api_terminal.publish_event`, the blockchain type is encoded into the topics:
```python
# from Brenthy/api_terminal/api_terminal.py

def publish_event(blockchain_type: str, payload: dict, topics: list = []):
	...
	for topic in topics:
		data = {"topic": f"{blockchain_type}-{topic}"}
		data.update(payload)
		publish_on_all_endpoints(data)
```

The actual code dealing with the pubsub sockets is still nested a few functions deeper inside, via `publish_on_all_endpoints()` which calls the `publish` functions of all the BrenthyAPI protocol modules (see [BrenthyAPI-Protocol](./BrenthyAPI-Protocol.md) for details).
This extra layer of complexity is due to Brenthy's [backward-compatibility-guarantee system](./BackwardCompatibilityGuarantee.md).

In summary, we have the same nested encapsulation for BrenthyAPI's event publication as for its requests.

Let's go through the process backwards, and look at the decapsulation of received events:

`brenthy_api`' provides the `EventListener` class for listening to to events published by a specific blockchain type.
We see in its event-handler function for processing received messages how it removes the encoded blockchain-type from the topics before passing on the event to the blockchain-type's event-handler:
```python
class EventListener():
    """Class for listening to the messages published by a blockchain type."""
	
    def __init__(
        self,
        blockchain_type: str,
        eventhandler: FunctionType,
        topics: str | list[str]
    ):
	    ...
	    brenthy_topics = [
            f"{self.blockchain_type}-{topic}" for topic in topics]
        ...
	
    def _handler(self, message, topic):
        """Process an event from Brenthy Core."""
        topic = topic.strip(f"{self.blockchain_type}-")
        ...
        self.users_eventhandler(message, topic)
```

Rising up from the depths of BrenthyAPI's infrastructure, let's look at how a blockchain API library uses the `brenthy_api`'s `EventListener` class to subscribe to publications from its blockchain.
Again, we see its event-handler remove the encoded blockchain ID from the topic, completing the decapsulation:
```python
# from Brenthy/blockchains/Walytis_Beta/walytis_beta_api/walytis_beta_interface.py

class BlocksListener:
    """A helper for the Blockchain class, taking care of calling Blockchain's
    block-received eventhandler whenever its blockchain receives a new block.
    """
    event_listener = None
    
    def __init__(self, blockchain_id: str, eventhandler, topics=[]):
	    ...
	    self.event_listener = brenthy_api.EventListener(
            "Walytis_Beta",
            self._eventhandler,
            f"{blockchain_id}-NewBlocks"
        )
    
    def _eventhandler(self, data: dict, topic: str):
        blockchain_topic = topic.strip(f"{self.blockchain_id}-")
```
