"""Run Brenthy."""

from func_monitoring import track_time
from apply_decorators import decorate_all_functions, decorate_class_methods
import atexit

from run import run_brenthy, stop_brenthy


from walytis_beta_tools._experimental.config import ipfs

decorate_class_methods(track_time, ipfs)

run_brenthy()
print("Press Ctrl+C to stop Brenthy.")
atexit.register(stop_brenthy)
