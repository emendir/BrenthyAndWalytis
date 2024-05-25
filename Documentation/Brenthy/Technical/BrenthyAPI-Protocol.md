_how `brenthy_api` and `api_terminal` work, including how they manage to achieve their [hyperintercompatibility](BackwardCompatibilityGuarantee.md)_

_**Prerequisite Knowledge**:_
_In [BrenthyAPI](BrenthyAPI.md) we saw how programs communicate with Brenthy to interact with blockchains, using `brenthy_api` on the application side and `api_terminal` on Brenthy's to do so._
_In [BackwardCompatibilityGuarantee](BackwardCompatibilityGuarantee.md) I explained why we want `brenthy_api` and Brenthy to eternally be fully backward compatible bidirectionally._

# BrenthyAPI-Protocol

BrenthyAPI is the infrastructure (coded in `api_terminal` and `brenthy_api`) which Brenthy provides to blockchains to allow them to communicate with their API libraries.
Blockchain API libraries send requests to their blockchains using the `brenthy_api` library which forwards the requests to `api_terminal` (a part of the core Brenthy software) which forwards it to the destination blockchain's request handler.
The BrenthyAPI Protocol (BAP) encompasses the specifics of how exactly `brenthy_api` and `api_terminal` communicate with each other, namely using TCP/IP [ZMQ sockets](https://zeromq.org/).

## BAP Versioning

BrenthyAPI's strategy for making sure that all versions of `brenthy_api` will be able to communicate with all versions of `api_terminal` is to keep each version of the code implementing the BrenthyAPI communication protocol (BAP for short) functional.
You can see these modules in in the source code in the folders `Brenthy/api_terminal/brenthy_api_protocols/` on Brenthy Core's side and in `Brenthy/brenthy_tools/brenthy_api_protocols/` on `brenthy_tools.brenthy_api`'s side.

```
Brenthy/api_terminal/brenthy_api_protocols/
├── bap_3_brenthy_core.py
└── bap_4_brenthy_core.py
```

```
Brenthy/brenthy_tools_beta/brenthy_api_protocols/
├── bap_3_brenthy_tools.py
└── bap_4_brenthy_tools.py
```

On `brenthy_tools.brenthy_api`'s side, the modules crucially define the `BAP_VERSION` constant, the `send_request(request)` function and the `EventListener` class.
On `api_terminal`'s side, the modules define the `BAP_VERSION` constant, the `handle_request(request)` & `publish(data)` functions, as well as `initialise()` and `terminate()` functions for runtime management.

Machinery common to multiple BrenthyAPI protocol versions is stored in `Brenthy/api_terminal/bat_endpoints.py` `api_terminal` and `Brenthy/brenthy_tools_beta/bt_endpoints.py` for `brenthy_tools.brenthy_api`.
These files contain some of the lowest level communication machinery in Brenthy's source code, using ZMQ and TCP websockets, as well as exception classes.
The different BAP version modules can use the functions and classes provided by these `bt_endpoints` modules in different ways, using the same underlying TCP/IP & ZMQ technology in to establish communication pathways of different qualities between `brenthy_api` and `api_terminal`.

## BAP Usage

Let's look at how `brenthy_api` and `api_terminal` use these BAP modules.

### `brenthy_tools.brenthy_api`

First of all, `brenthy_api` loads all the modules it finds in the `brenthy_api_protocols` folder. You can see this in the `load_brenthyapi_protocols()` function.

When an application wants to send a request, it tries all the different modules in order of novelty, until one succeeds in making the request.
Here's that code in `send_request()`:

```python
# from Brenthy/brenthy_tools_beta/brenthy_api.py
def send_request(blockchain_type: str, payload: bytearray | bytes) -> bytearray:
	...
	for protocol in bap_protocol_modules:
	    try:
	        reply = protocol.send_request(request)
	    except (CantConnectToSocketError, BrenthyReplyDecodeError):
	        # try next BrenthyAPI protocol
	        continue
	    break   # request sent, got reply,so move on
```

So when communicating with Brenthy, `brenthy_api` starts by trying to use the latest BAP version it has, and if it fails, it repeatedly tries again with the next latest BAP version until it succeeds via the latest BAP version which the Brenthy instance supports.

It follows the same strategy with the `EventListener` class, by which applications listen to messages published by `brenthy_core`.
Here's the code in the `brenthy_api`'s `EventListener` class' constructor:
```python
# from Brenthy/brenthy_tools_beta/brenthy_api.py

class EventListener():
	def __init__(
	...
	):
		...
		for protocol in bap_protocol_modules:
			try:
				eventlistener = protocol.EventListener(
					self._handler, brenthy_topics)
			except (CantConnectToSocketError, NotImplementedError):
				# try next BrenthyAPI protocol
				continue
			break   # EventListener connected
		self._eventlistener = eventlistener
```

When trying to connect to `api_terminal`'s publishing socket, `brenthy_api` tries connecting using the different BrenthyAPI protocol modules until one succeeds.

Thus `brenthy_tools.brenthy_api` achieves full backward compatibility with Brenthy Core.

### Brenthy Core's `api_terminal`

`api_terminal` also loads the modules it finds in its `brenthy_api_protocols` folder, in its `initialise()` function.

In `start_listening_for_requests()` it runs the `initialise()` function of each BAP module:

```python
# from Brenthy/api_terminal/api_terminal.py
def initialise():
	...
	for protocol in bap_protocol_modules:
	    protocol.initialise()
```

So essentially Brenthy always has its ears open to communication for all versions of BAP.
We can see that in the `bap_3_brenthy_core` module the `request_router()` function is imported from `api_terminal` and executed in the `handle_request()` function:

```python
# from Brenthy/api_terminal/brenthy_api_protocols/bap_3_brenthy_core.py
def handle_request(request):
	...
	reply = request_router(payload)
```

The `bap_4_brenthy_core` module does exactly the same thing, passing requests to the exact same function from `api_terminal` whenever it receives a request via its BrenthyAPI protocol.

And so every request, whatever BAP protocol it was transmitted via, is processed by the `api_terminal`, to be passed on to the correct blockchain (or the Brenthy requests handler).

When publishing messages, `api_terminal` publishes them using each BAP module, catering all versions of `brenthy_tools.brenthy_api`:

```python
# from Brenthy/api_terminal/api_terminal.py
def publish_on_all_endpoints(data: dict):
    for protocol in bap_protocol_modules:
        protocol.publish(data)
```

Thus Brenthy achieves full backward and forward compatibility with `brenthy_api`.
`brenthy_api` is backward compatible with all older versions of Brenthy, and Brenthy is backward compatible with all older versions of `brenthy_api`.
I call this eternal full bidirectional backward compatibility hyperintercompatibility for short.

## Blockchains

Now we've seen how Brenthy and `brenthy_api` achieve hyperintercompatibility.
That's great news for blockchains, because they don't have to worry about Brenthy versions.
It's great news for the user because they can happily let Brenthy update itself automatically whenever a new version is released.
But what the user cares about most is their applications, and what their applications care about most directly isn't Brenthy, but the blockchains.
In the end, it's up to the blockchain developers to implement hyperintercompatibility to provide their applications with the same quality that Brenthy provides them.
It's their audience, application developers, who won't want blockchains that are temporally unstable.

As the developer of Walytis, the blockchain Brenthy was originally built for, and which it depends upon, I declare that Walytis and its API are hyperintercompatible, and I'd rather make a new blockchain type than bring breaking changes to Walytis (which is why I'm using the blockchain name 'Walytis_Beta' for its initial release, so that I can still build breaking changes before I publish 'Walytis'!).
