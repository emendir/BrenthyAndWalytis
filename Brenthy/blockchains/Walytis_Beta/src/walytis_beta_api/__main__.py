"""Run Brenthy."""

import os
import sys

for i in range(3):
    os.chdir("..")
if os.path.basename(os.getcwd()) == "Brenthy":
    os.system(f"{sys.executable} .")
else:
    print(os.getcwd())
