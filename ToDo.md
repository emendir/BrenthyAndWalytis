## [Docs](Documentation/DocsRoadmap.md)
- contributions
- docs wiki?
- [x] double check BrenthyAPI and BrenthyAPI-Protocol

## Urgent Features

- [x] WalytisAPI make all communications JSON
- [x] when looking up unknown parent blocks, publish the parent block long IDs (is this necessary any more?) #phase4
- [X] get known nodes, sorted by activity #phase4
- [x] eradicate ancestry_traced, or make more room for future fields #phase4
- [x] BAP_X_BT don't have PubSub, fix? Rename those modules? #phase4
- [x] brenthy_tools manage timeouts, walytis_api show timeout error instead of no such blockchain
- [x] custom blockchain data path.
	  - update
	    - [/Documentation/Brenthy/Technical/Installation.md](/Documentation/Brenthy/Technical/Installation.md)
	    - [/Documentation/Brenthy/User/InstallingBrenthy.md](/Documentation/Brenthy/User/InstallingBrenthy.md)
	    - [/Documentation/Brenthy/User/ManualInstallation.md](/Documentation/Brenthy/User/ManualInstallation.md)
- [X] sort the parent block IDs before creating the parents' hash
- [X] `brenthy_updates` signature version and IPFS-CID
- [x] Deprecate BAP since TCP-Timeout is removed?
- [X] BAP_2: Is it a good idea to encode the BAP version in the TCP requests? (Too many versioning layers?)

### Code Cleanup

- [x] Brenthy-API-Reference: format code docstrings to support conversion #phase4


### API

- [ ] final check `walytis_api` API smoothness #phase4
- [x] streamline error messages

- [x] Blockchain._load_missed_blocks not hidden? #phase4
- [ ] Blockchain: pass directory #phase4
	- [x] implement
	- [ ] tests
	- [x] static function param
	- [x] docstrings
- [ ] check on efficiency of walytis_api.Blockchain._load_missed_blocks amount parameter
- [ ] fix issue with pip install not updating installed version of package, test for 2nd docker container
- [x] Bug:

```python
>>> import walytis_beta_api as wapi
>>> wapi.create_blockchain("test")
>>> bc = wapi.Blockchain("test", print)
>>> bc.add_block("hello there!".encode())
<walytis_beta_api.block_model.Block object at 0x71cd79197290>
<walytis_beta_api.block_model.Block object at 0x71cd79197350>
```


### Installation
- [ ] don't initialise IPFS as root
- [ ] install ipfs-monitor
## Tests:

- [x] test IPFS installation offer #phase4
- [ ] auto test installation on clean OSs #phase4

## Future Features

_Plan roadmap for following new features._

### DevOps

- [ ] for all essential tests, make them docker-only (remove role of the calling computer) #phase5
- [ ] ensure pytest compatibility of tests #phase5
### Features

- [ ] Option to change properties of invitations
- [ ] WalytisAPI: complex block queries (SQL?)
- [ ] local HTTP Server for access to blocks' contents
- [ ] Brenthy CLI
- [ ] Walytis CLI
- [ ] customisable log settings
- [ ] separate Walytis' logs from Brenthy's
- [ ] WalytisAPI latest block broadcasting: measure pubsub network latency

### Installation and update

- [ ] uninstall
- [ ] make Brenthy user system user with no login
- [ ] allow custom installation directory and data path
- [ ] allow individual blockchain instances to have their own data path
- [ ] test updates before installing them
- [ ] update immediately on reception as soon as no processes are running?
- [ ] after updating, systemctl shows status inactive (dead) even though Brenthy is running normally
- [ ] backup system which is not writeable by Brenthy user

### User-Friendliness

- [ ] walytis_api: print message when user uses blockchain name

## Security

- [ ] spam filters: disconnect from and blacklist nodes spamming on:
  - [ ] PubSub listener
  - [ ] join request listener
- [ ] forgery detection system for detecting composed lineages for achieving duplicate hashes
- [ ] blockchain types as malware against other blockchain types: blockchain types should not be able to access each others' appdata. create a user for each blockchain type?
- [ ] built-in monitoring for corrupt blocks

### Technical

- [ ] clean up threads from failed join requests
- [ ] BlockRecords: More efficient looking up and loading of recent blocks from a cache in memory, and from block storage as well?
- [ ] Walytis.get_blockchain_data: tests & documentation
- [ ] Brenthy and Brenthy-Tools: assert that maximum Brenthy API module protocol version is not greater than BAP version

### Code Cleanup
- [ ] remove all bare or broad exceptions #phase5
### Tests

- [ ] test for no ZMQ
- [ ] test inter-compatibility of different BrenthyAPI versions
- [ ] test all security functionality

### Control Panel Web-UI

_Everything_
