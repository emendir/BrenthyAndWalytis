import _testing_utils
from _testing_utils import mark, assert_exception
from brenthy_docker import BrenthyDocker, DockerShellTimeoutError, DockerShellError
import pytest
# @pytest.fixture(scope="module")
# def pt_docker_container():
#     return create_docker_container()
def test_preparations():
    print("Creating docker container...")
    pytest.docker_container =  BrenthyDocker()

def test_run_shell_command():
    command = "echo 'Hi 0'; sleep 1; echo 'Hi 1'"
    output = pytest.docker_container.run_shell_command(
        command,
        user=None,
        print_output=False,
        colour="light_yellow",
        background=False,
        timeout=5,
        ignore_errors=False,
    )
    assert "Hi 0" in output
    assert "Hi 1" in output

@pytest.mark.parametrize("print_output", [True, False])
def test_run_bash_code( print_output):
    bash_code = """
    #!/bin/bash
    for i in {0..2}; do
        echo "Iteration $i"
        sleep 1
    done
    echo "Done!"
    """
    output = pytest.docker_container.run_bash_code(
        bash_code,
        user=None,
        print_output=print_output,
        colour="light_yellow",
        background=False,
        timeout=5,
        ignore_errors=False,
    )
    assert "Iteration 0" in output
    assert "Iteration 2" in output
    assert "Done!" in output

@pytest.mark.parametrize("print_output", [True, False])
@pytest.mark.parametrize("timeout", [None, 5])
def test_run_python_code_normal( print_output, timeout):
    python_code = """
from time import sleep
for i in range(3):
    print(f"Iteration {i}")
    sleep(0)
print("Done!")
"""
    output = pytest.docker_container.run_python_code(
        python_code,
        user=None,
        print_output=print_output,
        colour="light_yellow",
        background=False,
        timeout=timeout,
        ignore_errors=False,
    )
    print(output)
    assert "Iteration 0" in output
    assert "Iteration 2" in output
    assert "Done!" in output

def test_run_python_code_timeout_error():
    python_code = """
from time import sleep
for i in range(3):
    print(f"Iteration {i}")
    sleep(1)
print("Done!")
"""
    success = assert_exception(
        DockerShellTimeoutError, "time",
        pytest.docker_container.run_python_code,
            python_code,
            user=None,
            print_output=True,
            colour="light_yellow",
            background=False,
            timeout=1,
            ignore_errors=False,
        )
    mark(success, "TimeoutError raised")


BREAKPOINTS = False
if __name__ == "__main__":
    args = [__file__, "-p", "no:terminalreporter"]  # -s disables output capturing
    if BREAKPOINTS:
        args.append("--pdb")
    pytest.main(args)
