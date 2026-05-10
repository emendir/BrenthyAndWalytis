"""Run Brenthy."""
# pylint: disable=invalid-name

import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
args_str = " ".join(sys.argv[1:])
os.system(f"{sys.executable} {os.path.join(SCRIPT_DIR, 'Brenthy')} {args_str}")
