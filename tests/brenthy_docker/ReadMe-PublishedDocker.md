# Brenthy-Testing Docker Image

This is a Ubuntu docker image with systemd, IPFS and Brenthy & Walytis installed, built for testing Brenthy & Walytis and applications built on them.

**See [Security Considerations](./ReadMe.md#security-considerations) below.**

## Running:

The simplest way to create and run a docker container of this image is:

```sh
docker run -d --name MY_BRENTHY_CONTAINER --privileged emendir/brenthy_testing
```

Log into your container's shell with:

```sh
docker exec -it MY_BRENTHY_CONTAINER /bin/bash
```

If you want you can run the container using the following command to watch the system boot up and log into its shell immediately, but it requires authenticating using the user `root` and password `password`:

```sh
docker run -it --privileged emendir/brenthy_testing
```

## Other Useful Commands

Get your docker container's IPFS peer ID:

```sh
echo $(docker exec MY_BRENTHY_CONTAINER ipfs id -f="<id>")
```

Check IPFS systemd service status:

```sh
docker exec -it MY_BRENTHY_CONTAINER systemctl status ipfs
```

## Interaction via Python

A dedicated python package, [`brenthy_docker`](https://pypi.org/project/brenthy-docker/), has been developed for working with these containers programmatically.
It provides the functionality of managing containers, transferring files into them and running python and bash code in them.

https://pypi.org/project/brenthy-docker/

## IPFS

To learn how IPFS is configured on this docker image and how to configure it further, see the documentation of its base image at
https://github.com/emendir/Docker-Systemd-IPFS?tab=readme-ov-file#ipfs

## Systemd

Docker containers don't usually use systemd, because they're intended to run a single process.
Running systemd inside a docker container allows the management of multilple processes as services, just like on most traditional Linux systems.

### Security Considerations

However, it's important to note that running systemd in a container introduces additional complexity and potential security risks.
The latter is due to the usage of the `--privileged` argument when running the container, which allows the container to have access to all the devices on the host as well as access to certain kernel capabilities that are typically restricted within containers.
Therefore, use this docker image judiciously and with a clear understanding of the implications for your specific use case.

As noted in the description, this docker image was designed for testing systemd-reliant applications, not productively running them.
