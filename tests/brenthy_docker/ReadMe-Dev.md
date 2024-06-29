# Docker Image Management

## `brenthy_prereqs` Docker Image

A docker container based on Ubuntu with all prerequisites installed.
It serves as a base image for the `brenthy_testing` docker image, so that the latter can be rebuilt offline and more quickly.

## `brenthy_testing` Docker Image

A docker container based on the local/brenthy_prereqs docker image.
That image installs all of the prerequisites, so that this image can be easily and quickly rebuilt offline.

# Workflow

## First Time:

1. Build the `brenthy_prereqs` docker image by running [build_brenthy_prereqs.sh](./build_brenthy_prereqs.sh).
2. Build the `brenthy_testing` docker image by running [build_brenthy_testing.sh](./build_brenthy_testing.sh).
3. Run a container with:
   ```sh
   docker run --privileged local/brenthy_testing
   ```

## Update Containers:

If you only made code changes that do not require installing new packages, you only need to rebuild the `brenthy_testing` image by running [build_brenthy_testing.sh](./build_brenthy_testing.sh)

If you did make code changes that require installing new packages:

1. Build the `brenthy_prereqs` docker image by running [build_brenthy_prereqs.sh](./build_brenthy_prereqs.sh).
2. Build the `brenthy_testing` docker image by running [build_brenthy_testing.sh](./build_brenthy_testing.sh).
