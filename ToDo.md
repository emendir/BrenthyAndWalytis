## [Docs](Documentation/DocsRoadmap.md)

## Urgent

- [ ] remove dependence on walytis_beta_tools._experimental
- [ ] new docker container using embedded IPFS node or separate IPFS container ⏫ 

## Repo-Organisation

- [ ] move /Brenthy/Docker and /Brenthy/InstallScripts to /deployement/
- [ ] rename /Brenthy to /src, /Documentation to /docs etc.
- [ ] For brenthy_testing, implement Multi-Stage Docker File instead of two files https://docs.docker.com/build/building/multi-stage/
- [ ] put all logs in /opt/Brenthy/logs
- [ ] split this todo list into separate lists for Brenthy & Walytis

## Docs

- BrenthyAPI port
- contributions
- docs wiki?

## Technical

### Core

- [ ] migrate from loguru to logging
- [ ] Brenthy and Brenthy-Tools: assert that maximum Brenthy API module protocol version is not greater than BAP version

### API

- [ ] fix `_load_brenthy_api_protocols_from_registry`

### Installation & Update

- [ ] don't initialise IPFS as root
- [ ] uninstall
- [ ] test updates before installing them
- [ ] update immediately on reception as soon as no processes are running?

### Debugging


## Tests:

- [ ] test for no ZMQ
- [ ] test inter-compatibility of different BrenthyAPI versions




## Security

- [ ] blockchain types as malware against other blockchain types: blockchain types should not be able to access each others' appdata. create a user for each blockchain type?

