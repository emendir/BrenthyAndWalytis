"""Machinery for managing and interacting with Brenthy docker containers.

You can run this script with: --name CONTATINER_NAME
"""

import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from types import FrameType

import ipfs_api


def get_option(option: str) -> str:
    """Get the specified option value from command line arguments."""
    try:
        return sys.argv[sys.argv.index(option) + 1]
    except:
        print("Invalid arguments.")
        sys.exit()


def delete_containers() -> None:
    """Delete all Brenthy docker containers."""
    os.system(
        "docker stop "
        "$(docker ps --filter 'ancestor=local/brenthy_testing' -aq) "
        ">/dev/null 2>&1; "
        "docker rm $(docker ps --filter 'ancestor=local/brenthy_testing' -aq) "
        ">/dev/null 2>&1"
    )
    os.system(
        "docker stop $(docker ps  --filter 'name=*brenthy*' "
        "--filter 'name= ^ brenthy' --filter 'name=brenthy$' -aq) "
        ">/dev/null 2>&1; "
        "docker rm $(docker ps --filter 'name=*brenthy*' "
        "--filter 'name= ^ brenthy' --filter 'name=brenthy$' -aq) "
        ">/dev/null 2>&1"
    )


class BrenthyDockerContainer:
    """Represents a Brenthy docker container."""

    container_id = ""
    container_name = ""

    def __init__(
        self,
        container_name: str,
        auto_run: bool = True,
        container_id: str | None = None,
    ):
        """Create an object to represent a docker container.

        If `container_id` is not passed, creates a new docker container
        """
        self.container_name = container_name
        if auto_run:
            self.run()
        elif container_id:
            self.container_id = container_id
            self.ipfs_id = ""

            while self.ipfs_id == "":
                self._docker_swarm_connect()
                self.ipfs_id = self.run_shell_command('ipfs id -f="<id>"')
                time.sleep(1)

    def run(self) -> None:
        """Start this docker container."""
        threading.Thread(
            target=self._run_docker,
            args=(),
            name=f"Docker-{self.container_name}",
        ).start()
        time.sleep(1)

        # getting container id from container name
        while not self.container_id:
            time.sleep(1)
            # getting container id from container name
            result = subprocess.run(
                f'docker ps -aqf "name=^{self.container_name}$"',
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            )
            self.container_id = result.stdout.strip("\n")

        self.ipfs_id = ""

        # wait till IPFS is running and till we can reach it
        while not self.ipfs_id or not ipfs_api.find_peer(self.ipfs_id):
            time.sleep(1)
            self._docker_swarm_connect()
            self.ipfs_id = subprocess.run(
                (
                    f"docker exec -it {self.container_id} "
                    'ipfs id -f="<id>" 2>/dev/null'
                ),
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            ).stdout

    def log(self) -> None:
        """Open the docker container's Brenthy log in gedit."""

        def _open_brenthy_log() -> None:
            command = "su brenthy -c '/usr/bin/cat /opt/Brenthy/Brenthy.log'"
            log_text = self.run_shell_command(command)

            with tempfile.NamedTemporaryFile() as tp:
                tp.write(log_text.encode())
                tp.flush()
                command = f"gedit {tp.name}"
                subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                )

        threading.Thread(target=_open_brenthy_log, args=()).start()

    def run_python_code(
        self,
        python_code: str,
        hide_error: bool = False,
        brenthy_user: bool = False,
        print_command: bool = False,
    ) -> str:
        """Run python code from within the container's operating system."""
        command = (
            'python3 -c \\"' + python_code.replace('"', '\\\\\\"') + '\\"'
        )
        if brenthy_user:
            command = f'su brenthy -c "{command}"'
        else:
            command = f'su -c "{command}"'
        command = f"docker exec -it {self.container_id} {command}"
        if print_command:
            print("Running python code in Docker container:")
            print(command)
        # breakpoint()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            # check=True
        )
        if not hide_error and result.stdout.startswith(
            "Traceback (most recent call last):\n"
        ):
            print(result.stdout)
            # breakpoint()
        return result.stdout

    def run_shell_command(
        self, command: str, brenthy_user: bool = False, check: bool = True
    ) -> str:
        """Run shell code from within the container's operating system."""
        command = command.replace("'", "'").replace('"', '"')
        if brenthy_user:
            command = f"su brenthy -c '{command}'"
        command = f"docker exec -it {self.container_id} {command}"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout

    def __run_host_shell_command(self, cmd: str) -> tuple[str, str]:
        """Run shell code from within this operating system."""
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return (result.stdout, result.stderr)

    def stop(self) -> None:
        """Stop this docker container."""
        if self.container_id:
            os.system(f"docker stop {self.container_id}  >/dev/null 2>&1")

    def restart(self) -> None:
        """Restart this docker container."""
        if self.container_id:
            os.system(f"docker restart {self.container_id}  >/dev/null 2>&1")
            # wait till IPFS is running
            while not subprocess.run(
                (
                    f"docker exec -it {self.container_id} "
                    'ipfs id -f="<id>" 2>/dev/null'
                ),
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            ).stdout:
                time.sleep(1)
            # wait till we can connect to docker via IPFS
            while not ipfs_api.find_peer(self.ipfs_id):
                pass
        else:
            self.run()

    def login(self) -> None:
        """Copy a shell command to log in to this docker container's shell."""
        import pyperclip

        command = f"docker exec -it {self.container_id} /bin/bash"
        pyperclip.copy(command)
        print(command)
        print("Command copied to clipboard.")

    def terminate(self) -> None:
        """Stop and remove this docker container."""
        if self.container_id:
            self.__run_host_shell_command(
                f"docker stop {self.container_id}  >/dev/null 2>&1"
            )
            self.__run_host_shell_command(
                f"docker rm {self.container_id}  >/dev/null 2>&1"
            )

    def _run_docker(self) -> None:
        """Create and run a Brenthy docker container."""
        os.system(
            "docker run --cap-add SYS_ADMIN --privileged "
            f"--name {self.container_name} local/brenthy_testing "
            ">/dev/null 2>&1"
        )

    def _docker_swarm_connect(self) -> None:
        """Try to connect to this docker container via IPFS."""
        # Out of all our IPFS multi-addresses, choose the first non-localhost
        # IP address for both IPv4 & IPv6, and get the our multi_addresses for
        # those IP-addresses for both UDP & TCP
        multi_addresses = dict(ipfs_api.http_client.id())["Addresses"]
        ip6_tcp_maddr = [
            address
            for address in multi_addresses
            if address.startswith("/ip6/")
            and not address.startswith("/ip6/::1/")
            and address.split("/")[3] == "tcp"
        ]
        ip6_udp_maddr = [
            address
            for address in multi_addresses
            if address.startswith("/ip6/")
            and not address.startswith("/ip6/::1/")
            and address.split("/")[3] == "udp"
        ]
        ip4_tcp_maddr = [
            address
            for address in multi_addresses
            if address.startswith("/ip4/")
            and not address.startswith("/ip4/127.0.0.1/")
            and address.split("/")[3] == "tcp"
        ]
        ip4_udp_maddr = [
            address
            for address in multi_addresses
            if address.startswith("/ip4/")
            and not address.startswith("/ip4/127.0.0.1/")
            and address.split("/")[3] == "udp"
        ]
        commands = []
        if ip6_tcp_maddr:  # if any such addresses were found, try to connect
            commands.append(f"ipfs swarm connect {ip6_tcp_maddr[0]}")

        if ip6_udp_maddr:  # if any such addresses were found, try to connect
            commands.append(f"ipfs swarm connect {ip6_udp_maddr[0]}")

        if ip4_tcp_maddr:  # if any such addresses were found, try to connect
            commands.append(f"ipfs swarm connect {ip4_tcp_maddr[0]}")

        if ip4_udp_maddr:  # if any such addresses were found, try to connect
            commands.append(f"ipfs swarm connect {ip4_udp_maddr[0]}")

        self.run_shell_command(" & ".join(commands), check=False)

        # print(f"ipfs swarm connect {ip6_tcp_maddr}")
        # print(f"ipfs swarm connect {ip6_udp_maddr}")
        # print(f"ipfs swarm connect {ip4_tcp_maddr}")
        # print(f"ipfs swarm connect {ip4_udp_maddr}")


if __name__ == "__main__":
    if "--name" in sys.argv:
        container_name = get_option("--name")
    else:
        container_name = "manually_created"
    docker_container = BrenthyDockerContainer(container_name)

    def _signal_handler(sig: int, frame: FrameType | None) -> None:
        docker_container.terminate()
        sys.exit(0)

    # Handle Ctrl+C (SIGINT), shutting down docker container
    signal.signal(signal.SIGINT, _signal_handler)
    signal.pause()
