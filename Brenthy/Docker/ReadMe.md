## Brenthy Docker Image

A `brenthy` docker container requires access to IPFS from another source, such as from the container's host or another docker container.

### Example Usage with Docker Compose
The `docker-compose.yml` file demonstrates how a Brenthy docker container can be orchestrated together with an IPFS docker container and another docker container that hosts a Brenthy Application.

To run this example, run this shell command from this directory:
```sh
docker compose run DEMO_BRENTHY_APP
```
This will run an IPFS container, a Brenthy container, and a demo-Brenthy-app container that, after installing the `walytis_beta_api` python package, opens a python shell in which you can interact with Brenthy and Walytis.

### Limitations
- Join given invitation doesn't work, but join from ZIP or CID does