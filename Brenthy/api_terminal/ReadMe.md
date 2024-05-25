This directory contains all the machinery needed for Brenthy to interact with applications via BrenthyAPI.  
The machinery for applications to communicate with Brenthy via BrenthyAPI is stored in [../brenthy_tools_beta](../brenthy_tools_beta).

The complexity of this `api_terminal` arises from this project's tenet of always providing full two-way backward-compatibility between `brenthy_api` and Brenthy.
This means that all deprecated BrenthyAPI protocols are preserved and will always be available on Brenthy and `brenthy_api`.

To organise this collection of old and new code, we have the following module structure in the `api_terminal` subpackage:

### `api_terminal` SubPackage Structure:
- **api_terminal.py:** provides the interface of the `api_terminal` subpackage for Brenthy.
- **endpoints.py:** contains all the websocket-level communication machinery used by all versions of BrenthyAPI, ie. different functions and classes for publishing events and receiving & replying to requests via ZMQ & TCP sockets
- **protocols:** a folder which contains multiple python modules, each containing new ways of using the machinery in `endpoints` to communicate with `brenthy_api`. For example, the protocol modules `v0_1_0` and `v0_1_1` contain machinery that encodes the BrenthyAPI version they use in every message they send via TCP or ZMQ sockets from `endpoints` to `brenthy_api`, but while `v0_1_0` processes requests from `brenthy_api` sequentially, `v0_1_1` can process multiple requests in parallel. 

### BrenthyAPI Protocol Version (BAP)
Not to be confused with the brenthy_api version:
- **brenthy_api version:** the version of the `brenthy_api` package.
- **BrenthyAPI protocol version:** the identifier of a communication protocol between Brenthy and `brenthy_api`
