"""Rebuild the brenthy-test docker image.

DON'T FORGET to update the brenthy_prereqs docker image
if you've introduced new dependency packages!
"""

import os

from termcolor import colored as coloured


def build_docker_image(verbose: bool = True) -> None:
    """Rebuild the brenthy-test docker image."""
    print(
        coloured(
            (
                "DON'T FORGET to update the brenthy_prereqs docker image "
                "if you've introduced new dependency packages!"
            ),
            "yellow",
        )
    )
    print("Building docker image...")

    args_str = ""
    if not verbose:
        args_str += " >/dev/null"
    builder_script_path = os.path.join(
        os.path.dirname(__file__), "build_brenthy_testing.sh"
    )
    exit_code = os.system(builder_script_path + args_str)
    if exit_code != 0:
        print(coloured("Docker image udpate failed!", "red"))
        raise Exception("Docker image udpate failed!")


if __name__ == "__main__":
    build_docker_image()
