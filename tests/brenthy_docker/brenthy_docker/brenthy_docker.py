import uuid
import io
import os
import shutil
import sys
import tarfile
import tempfile
from time import sleep

import docker
from _testing_utils import ipfs
import pexpect
import pyperclip
from termcolor import colored as coloured


class DockerShellError(Exception):
    """When a shell command run in the docker container produces an Exception."""

    def __init__(self, exit_status: int, shell_output: str):
        self.exit_status = exit_status
        self.shell_output = shell_output

    def __str__(self):
        return "\n".join([
            "The shell command run in the docker container errored.",
            f"Exit Status: {self.exit_status}",
            "Output:",
            f"{self.shell_output}"
        ])


class BrenthyDocker:
    def __init__(
        self,
        image: str = "emendir/brenthy_testing",
        container_name: str = "",
        container_id: str | None = None,
        auto_run: bool = True,
        await_brenthy: bool = True,
        await_ipfs: bool = True
    ):
        self._docker = docker.from_env()
        self.ipfs_id = ""

        if container_id:
            self.container = self._docker.containers.get(container_id)
        else:
            self.container = self._docker.containers.create(
                image, privileged=True, name=container_name
            )
        self.docker_id = self.container.id
        if auto_run:
            self.start(
                await_brenthy=await_brenthy,
                await_ipfs=await_ipfs,
            )

    @property
    def name(self):
        return self.container.name

    @property
    def container_id(self):
        return self.container.id

    def start(
        self, await_brenthy: bool = True, await_ipfs: bool = True
    ) -> None:
        """Start this container."""
        self.container.start()

        if await_brenthy:
            # print("Awaiting BrenthyUpdatesTEST switch...")
            # wait till docker container's Brenthy has renamed its update blockhain
            # and restarted
            while not self.run_python_command(
                ("import os;"
                 "print(os.path.exists('/opt/Brenthy/BlockchainData/Walytis_Beta/BrenthyUpdatesTEST'))"),
                print_output=False
            ) == "True":
                sleep(0.2)
            sleep(0.2)
        if await_ipfs:
            # print("Awaiting IPFS init...")
            self.ipfs_id = ""

            while not (self.ipfs_id and ipfs.peers.find(self.ipfs_id)):
                try:
                    self.ipfs_id = self.run_shell_command(
                        'ipfs id -f="<id>"', print_output=False)
                except:
                    pass
                if self.ipfs_id:
                    self._docker_swarm_connect()
                sleep(1)
        # print("BrenthyDocker started!")

    def stop(self, force=False) -> None:
        """Stop this container."""
        if force:
            self.container.stop(timeout=0)
        else:
            self.container.stop()

    def restart(self) -> None:
        """Restart this container."""
        self.container.restart()

        # why is this necessary? Seems to sometimes work without...
        self.run_shell_command("systemctl start ipfs")

    def delete(self, force=False) -> None:
        if force:
            self.container.stop(timeout=0)
        else:
            self.run_bash_code("poweroff")
            self.container.stop()
        self.container.remove()

    def transfer_file(self, local_filepath: str, remote_filepath: str) -> None:
        """Copy a local file into the docker container."""
        dst_dir = os.path.dirname(remote_filepath)
        stream = io.BytesIO()
        with (
            tarfile.open(fileobj=stream, mode='w|') as tar,
            open(local_filepath, 'rb') as f
        ):
            info = tar.gettarinfo(fileobj=f)
            info.name = os.path.basename(remote_filepath)
            tar.addfile(info, f)
        # create remote directory if needed
        self.run_shell_command(
            f"mkdir -p {os.path.dirname(remote_filepath)}", print_output=False)
        self.container.put_archive(dst_dir, stream.getvalue())


    def write_to_tempfile(self, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")

        filename = f"temp_{uuid.uuid4().hex[:12]}"
        local_tempdir = tempfile.mkdtemp()
        local_path = os.path.join(local_tempdir, filename)
        remote_path = f"/opt/tmp/{filename}"

        try:
            # Write and flush to ensure file exists on disk
            with open(local_path, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            if not os.path.exists(local_path):
                raise RuntimeError(f"Local temp file was not created: {local_path}")

            # Transfer to container and check for success
            transfer_result = self.transfer_file(local_path, remote_path)

            # Optional: Run `ls` in the container to confirm file landed
            check_result = self.run_shell_command(f"ls {remote_path}", print_output=False, ignore_errors=True)
            if remote_path not in check_result:
                raise RuntimeError(f"File does not appear to exist in container after transfer: {remote_path}")

            return remote_path

        finally:
            # Important: Delay deletion until after transfer
            shutil.rmtree(local_tempdir, ignore_errors=True)
    def is_running(self) -> bool:
        """Check if this docker container is running or not."""
        return self._docker.containers.get(
            self.container.id
        ).attrs["State"]["Running"]

    def run_shell_command(
        self,
        command: str,
        user: str | None = None,
        print_output: bool = True,
        colour: str = "light_yellow",
        background: bool = False,
        timeout: int = 10,
        ignore_errors=False
    ) -> str:
        """Run shell code from within the container's operating system.

        Not suitable for code that contains double quotes.

        Args:
            command:
            user:
            print_output:
            colour:
            background:
            timeout: currently only implemented for print_output==True
        """
        if print_output and background:
            print(
                "Parameters `print_output` and `background` "
                "can't both be `True`. Deactivating `print_output`."
            )
            print_output = False

        if user:
            command = f"su {user} -c \"{command}\""

        if print_output:
            return self.run_shell_command_printed(
                command, print_output=True, colour=colour, timeout=timeout
            )

        if background:
            command = f"nohup {command} > /dev/null 2>&1 &"
        ex_id = self._docker.api.exec_create(self.container.id, command)['Id']
        output = self._docker.api.exec_start(
            ex_id, tty=False, detach=background
        )
        if background:
            return ""
        output_str = output.strip().decode()

        exec_info = self._docker.api.exec_inspect(ex_id)
        exit_status = exec_info['ExitCode']
        if not ignore_errors and exit_status != 0:
            raise DockerShellError(exit_status, output_str)

        return output_str

    def run_shell_command_printed(
        self,
        command: str,
        print_output: bool = True,
        colour: str = "light_yellow",
        timeout: int = 10
    ) -> str:
        """Run shell code from within the container's operating system.

        Not suitable for code that contains double quotes.

        Args:
            command
            print_output
            colour
            timeout: currently only implemented for print_output==True
        """
        command = f"docker exec -it {self.container.id} {command}"
        result = ""

        try:
            child = pexpect.spawn(command, encoding='utf-8',
                                  timeout=timeout, logfile=sys.stdout)

            while True:
                try:
                    line = child.readline()
                    if not line:
                        break
                    if print_output:
                        if colour:
                            print(coloured(line.strip(), colour))
                        else:
                            print(line.strip())
                    result += line
                except pexpect.exceptions.TIMEOUT:
                    print(coloured(
                        "WARNING (BrenthyDocker): "
                        "Docker shell command timeout reached for command\n"
                        f"{command}",
                        "red"
                    ))
                    break
                except pexpect.EOF:
                    break

            # Ensure the process has finished
            if child.isalive():
                child.close()

        except Exception as e:
            print(coloured(f"ERROR (BrenthyDocker): {str(e)}", "red"))
        # result = subprocess.run(
        #     command, shell=True, capture_output=True, text=True, check=check
        # )
        return result.strip()

    def run_bash_code(
        self,
        code: str | list[str],
        print_output: bool = True,
        colour: str = "light_yellow",
        background: bool = False,
        timeout: int = 10,
        ignore_errors: bool = False


    ) -> str:
        """Run any bash code in the docker container, returning its output.

        Suitable for code that contains any quotes and escape characters.

        Args:
            code
            print_output
            colour
            background
            timeout: currently only implemented for print_output==True
        """
        if isinstance(code, list):
            # concatenate list elements into single string
            code = "\n".join(code)
        remote_tempfile = self.run_shell_command(
            "mktemp", print_output=False).strip()
        return self.run_shell_command(
            f"/bin/bash {remote_tempfile}",
            print_output=print_output, colour=colour, background=background,
            timeout=timeout, ignore_errors=ignore_errors
        )

    def run_python_command(
        self,
        command: str,
        print_output: bool = True,
        colour: str = "light_yellow",
        background: bool = False,
        timeout: int = 10,
        ignore_errors: bool = False

    ) -> str:
        """Run single-line python code, returning its output.

        Not suitable for code that contains double quotes.

        Args:
            command
            print_output
            colour
            background
            timeout: currently only implemented for print_output==True
        """
        python_command = "python -c \"" + command + "\""
        return self.run_shell_command(
            python_command,
            print_output=print_output, colour=colour, background=background,
            timeout=timeout, ignore_errors=ignore_errors
        )

    def run_python_code(
        self,
        code: str | list[str],
        print_output: bool = True,
        colour: str = "light_yellow",
        background: bool = False,
        timeout: int = 10,
        ignore_errors: bool = False,

    ) -> str:
        """Run any python code in the docker container, returning its output.

        Suitable for code that contains any quotes and escape characters.

        Args:
            code
            print_output
            colour
            background
            timeout
        """
        if isinstance(code, list):
            # concatenate list elements into single string
            code = "\n".join(code)
        remote_tempfile = self.write_to_tempfile(code)
        return self.run_shell_command(
            f"/bin/python {remote_tempfile}",
            print_output=print_output, colour=colour, background=background,
            timeout=timeout, ignore_errors=ignore_errors
        )

    def _docker_swarm_connect(self) -> None:
        """Try to connect to this docker container via IPFS."""
        # Out of all our IPFS multi-addresses, choose the first non-localhost
        # IP address for both IPv4 & IPv6, and get the our multi_addresses for
        # those IP-addresses for both UDP & TCP
        multi_addresses = ipfs.get_addrs()
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
        try:
            self.run_bash_code(" & ".join(commands), print_output=False)
        except:
            pass

        # print(f"ipfs swarm connect {ip6_tcp_maddr}")
        # print(f"ipfs swarm connect {ip6_udp_maddr}")
        # print(f"ipfs swarm connect {ip4_tcp_maddr}")
        # print(f"ipfs swarm connect {ip4_udp_maddr}")
    def login(self) -> None:
        """Copy a shell command to log in to this docker container's shell."""
        command = f"docker exec -it {self.container.id} /bin/bash"
        pyperclip.copy(command)
        print(command)
        print("Command copied to clipboard.")


def delete_containers(
    image: str = "", container_name_substr: str = ""
) -> None:
    """Delete all docker containers of the given image or name.

    Any docker image with the given image name in their image ancestry OR
    containing `container_name_substr` in its container name
    will be deleted.
    """
    if image:
        os.system(
            "docker stop "
            f"$(docker ps --filter 'ancestor={image}' -aq) "
            ">/dev/null 2>&1; "
            f"docker rm $(docker ps --filter 'ancestor={image}' -aq) "
            ">/dev/null 2>&1"
        )
    if container_name_substr:
        os.system(
            "docker stop $(docker ps  "
            f"--filter 'name=*{container_name_substr}*' "
            f"--filter 'name= ^ {container_name_substr}' "
            f"--filter 'name={container_name_substr}$' "
            f"--filter 'name={container_name_substr}*' "
            "-aq) >/dev/null 2>&1; "
            "docker rm $(docker ps "
            f"--filter 'name=*{container_name_substr}*' "
            f"--filter 'name= ^ {container_name_substr}' "
            f"--filter 'name={container_name_substr}$' "
            f"--filter 'name={container_name_substr}*' "
            "-aq) >/dev/null 2>&1"
        )


class ContainerNotRunningError(Exception):
    """When the container isn't running."""


# Example usage:
if __name__ == "__main__":
    # Create an instance of DockerContainer with the desired image
    delete_containers(container_name_substr="DemoBrenthy")
    docker_container = BrenthyDocker(
        container_name="DemoBrenthy",
        auto_run=False
    )

    container_id = docker_container.container.id
    # Start the container
    docker_container.start(await_brenthy=False, await_ipfs=True)

    print("Container's IPFS ID: ", docker_container.ipfs_id)

    # Execute shell command on the container
    shell_output = docker_container.run_shell_command(
        "systemctl status brenthy")
    print("Output of Shell command:", shell_output)

    # Execute Python command on the container
    python_output = docker_container.run_python_command(
        "import walytis_beta_api;"
        "print(walytis_beta_api.get_walytis_beta_version())"
    )
    print("Output of Python command:", python_output)

    docker_container.transfer_file(
        "brenthy_docker.py", "/tmp/test/wad.py")
    docker_container.run_shell_command("ls /tmp/test/")

    remote_tempfile = docker_container.write_to_tempfile("Hello there!")
    docker_container.run_shell_command(f"cat {remote_tempfile}")
    # Stop the container
    docker_container.stop()

    docker_container = BrenthyDocker(container_id=container_id)
    docker_container.start()
    shell_output = docker_container.run_shell_command(
        "systemctl status brenthy")
    print("Output of Shell command:", shell_output)
    docker_container.stop()
