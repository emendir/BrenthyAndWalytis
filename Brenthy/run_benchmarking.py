"""Run Brenthy."""

from func_monitoring import track_time
from decorate_all import decorate_all_functions
import atexit

from run import run_brenthy, stop_brenthy


import ipfs_api

decorate_all_functions(track_time, ipfs_api.__name__)

run_brenthy()
print("Press Ctrl+C to stop Brenthy.")
atexit.register(stop_brenthy)
