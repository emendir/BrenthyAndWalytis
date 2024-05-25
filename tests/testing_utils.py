from tqdm import tqdm, TMonitor
import threading
from termcolor import colored as coloured
import time

BREAKPOINTS = False


def mark(success):
    """Returns a check or cross character depending on the input success."""
    if success:
        mark = coloured("✓", "green")
    else:
        mark = coloured("✗", "red")
        if BREAKPOINTS:
            breakpoint()
    return mark


def test_threads_cleanup():
    for _ in range(2):
        polite_wait(5)
        threads = [
            x for x in threading.enumerate() if not isinstance(x, TMonitor)
        ]
        success = len(threads) == 1
        if success:
            break
    print(mark(success), "thread cleanup")
    if not success:
        [print(x) for x in threads]


def polite_wait(n_sec: int):
    # print(f"{n_sec}s patience...")
    for i in tqdm(range(n_sec), leave=False):
        time.sleep(1)
