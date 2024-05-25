How?
- python .
- import run;run.run_brenthy()
It all starts in the run.py module.

What happens?
- Run.py
  - check/offer installation
  - run updates blockchain
  - wait for IPFS
  - start blockchain_manager
  - start api_terminal
- blockchain_manager.py
  - checks and loads blockchain types
  - commands each blockchain type run its blockchains