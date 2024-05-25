"""Run Brenthy."""

import atexit

from run import run_brenthy, stop_brenthy

run_brenthy()
print("Press Ctrl+C to stop Brenthy.")
atexit.register(stop_brenthy)
