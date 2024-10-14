## [Docs](Documentation/DocsRoadmap.md)

- contributions
- docs wiki?

## Technical

### Core

- [ ] Make `walytis_beta_api` capable of fully verifying a blockchain from block data files, so that the role of Walytis Core is only creating and sharing blocks.
- [ ] Join Blockchain timeout when no data has been received during file transmission
- [ ] Remove `block_records` block index? Make more efficient?
- [ ] clean up threads from failed join requests
- [ ] Walytis.get_blockchain_data: tests & documentation
- [ ] Brenthy and Brenthy-Tools: assert that maximum Brenthy API module protocol version is not greater than BAP version

### API

- [ ] Blockchain: pass directory #phase4
  - [x] implement
  - [ ] tests
  - [x] static function param
  - [x] docstrings
- [ ] check on efficiency of `walytis_api.Blockchain._load_missed_blocks` amount parameter
- [ ] fix issue with pip install not updating installed version of package, test for 2nd docker container
- [ ] proper error message when IPFS is turned off
- [ ] Blockchain only remembers if user's block handler processed the block if update_blockids_before_handling == False
- [ ] Blockchain: replace `auto_load_missed_blocks` with `auto_start_block_handling`
- [ ] add replacement for `get_latest_blocks` which automatically uses long IDs

### Installation

- [ ] don't initialise IPFS as root
- [ ] install ipfs-monitor
- [ ] remove pip github installation of eciespy when ready
- [ ] don't hardcode version of PyPy

## Tests:

- [ ] add docstrings to Brenthy/blockchains/Walytis_Beta/walytis_beta_api/generic_blockchain_testing.py
- [ ] auto test installation on clean OSs #phase4
- [ ] test for no ZMQ
- [ ] test inter-compatibility of different BrenthyAPI versions
- [ ] test all security functionality
- [ ] test for performance metrics
- [ ] find out scalability limits, expand and test them

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

## Code Cleanup

- [ ] remove all bare or broad exceptions #phase5

## Control Panel Web-UI

_Everything_
