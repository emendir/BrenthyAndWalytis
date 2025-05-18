_the mechanisms behind nodes becoming new members of existing blockchains_
# Joining Blockchains
## Conceptual Background

The first types of blockchains each had one universal instance of the blockchain, initialised by the developer.
Walytis differs from that, because Walytis applications create new instances of the blockchain for their own specific use cases whenever needed.

An instance of a Walytis blockchain is created by one node.
After creation, then, other nodes must have a way of getting access to the blockchain.
The process of a node getting access to and becoming a member and participant of a blockchain is called _joining_.

## The Joining Process
_To learn how to get a node to join a blockchain in practice, see the tutorial [2 - Joining Blockchains](/Documentation/Walytis/Tutorials/2-JoiningBlockchains.md)_

1. To enable another node to join a Walytis blockchain, an existing member (e.g. the blockchain creator) creates an invitation at the application level using the Walytis API. Creating an invitation returns invitation code, which is a JSON string that encodes the technical information necessary for another node to join the blockchain:
	- blockchain ID
	- IPFS peer IDs of existing nodes
	- key for basic authentication
	- whether or not the key is reusable
	- whether or not the joining node should share the key and allow new nodes to join
2. The invitation creator (and joiners in the case of shared invitation codes) listen for incoming join requests.
3. The invitation creator's application or human user shares the invitation code with the new node that wants to join the blockchain.
4. At the application layer, the new node uses the Walytis API to send a join request to an existing node on the blockchain using the invitation code.
5. When an existing node receives a join request, it checks if it knows the invitation code's key, and if so, transmits its blockchain appdata, i.e. the blockchain's blocks, to the requesting node.
6. Knowing the blockchain's blocks, the join-requester can now be an active member of the blockchain.  

## Security

Walytis currently doesn't have a fully-fledged secure authentication system for joining.
The invitation code's primary function is to enable joining, not limit it.
The security of the invitation-code-key authentication lies in the responsibility of all nodes who hold and transmit it.
Since Walytis, like most blockchains, doesn't have a way of controlling its members, building a more secure way of authenticating the joining of new nodes is probably of little use, as a single malicious node breaching this more advanced security would open the gates to allow any amount of other nodes to join.

### Using Private IPFS Networks

Using a private IPFS network would add a second layer of basic security, allowing only nodes on the same private IPFS network to communicate with each other.
While again, this doesn't provide very advanced security and again, it relies on the responsibility of all nodes who hold and transmit the key (in this case the private IPFS network key), it would be useful as a defence against DOS-attacks on the join-request listener from malicious actors searching for random victims.
