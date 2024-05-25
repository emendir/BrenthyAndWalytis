"""Run Brenthy."""
# pylint: disable=invalid-name

import os
import sys

args_str = " ".join(sys.argv[1:])
os.system(f"{sys.executable} ./Brenthy {args_str}")
