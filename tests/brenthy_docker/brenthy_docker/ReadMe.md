# Brenthy Docker Python Package

This package contains a `BrenthyDocker` class for interacting with docker containers running IPFS and Brenthy.
It contains useful methods for managing containers, transferring files into them and running python and bash code in them.

The main use-case for this class is for automated tests of Brenthy's blockchains and the applications built on them.

## Usage

### Simplest

```python
from brenthy_docker import BrenthyDocker, delete_containers
docker_container = BrenthyDocker()
```

By default, `BrenthyDocker` creates a container based on the [`emendir/brenthy_testing`](https://hub.docker.com/r/emendir/brenthy_testing) image.
You can, however, specify a custom image name, using:

```python
docker_container = BrenthyDocker(image="local/MyWalytisApp")
```

### Features Demo

The following python snippet demonstrates most of `BrenthyDocker`'s features.

```python
from brenthy_docker import BrenthyDocker, delete_containers

# remove any uncleanedup containers
delete_containers(container_name_substr="Brenthy-Demo")

print("Creating docker container, waiting to connect to it via IPFS...")
docker_container = BrenthyDocker(
    image="emendir/brenthy_testing"
    container_name="Brenthy-Demo",
    # await_brenthy=False,  # don't wait till Brenthy has fully initialised
    # await_ipfs=False,    # don't wait till we've established an IPFS connection to the docker container
)

print("Container ID:", docker_container.container.id)
print("Container's IPFS ID:", docker_container.ipfs_id)

# Execute shell command on the container
shell_output = docker_container.run_shell_command(
    "systemctl status brenthy",
    print_output=False
)

print("Output of Shell command:", shell_output)

# Execute Python command on the container
python_output = docker_container.run_python_command(
    "import walytis_beta_api;print(walytis_beta_api.get_walytis_beta_version())",
    print_output=True,
    colour="green"
)
print("Output of Python command:", python_output)

docker_container.transfer_file("brenthy_docker.py", "/tmp/test/wad.py")
docker_container.run_shell_command("ls /tmp/test/")

remote_tempfile = docker_container.write_to_tempfile("Hello there!")
docker_container.run_shell_command(f"cat {remote_tempfile}")
# Stop the container
docker_container.stop()
```
