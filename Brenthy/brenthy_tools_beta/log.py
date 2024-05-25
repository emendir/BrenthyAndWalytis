"""Custom logging manager for Brenthy."""

import os
import shutil
import traceback
from datetime import datetime
from threading import Lock
from typing import Literal

COLOUR_TYPES = (
    Literal[
        "black",
        "grey",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "light_grey",
        "dark_grey",
        "light_red",
        "light_green",
        "light_yellow",
        "light_blue",
        "light_magenta",
        "light_cyan",
        "white",
    ]
    | None
)

try:
    from termcolor import colored

    def coloured(text: str, colour: COLOUR_TYPES) -> str:
        """Print coloured text."""
        return colored(text, colour)
except ModuleNotFoundError:

    def coloured(text: str, colour: COLOUR_TYPES) -> str:
        """Nonfunctional dummy function for when termcolor is not installed."""
        return text


PRINT_INFO = False
PRINT_IMPORTANT = True
PRINT_DEBUG = True
PRINT_WARNING = True
PRINT_ERROR = True
PRINT_FATAL = True

RECORD_INFO = True
RECORD_IMPORTANT = True
RECORD_DEBUG = True
RECORD_WARNING = True
RECORD_ERROR = True
RECORD_FATAL = True

LOG_ERROR_TRACEBACK = True
LOG_FATAL_TRACEBACK = True

LOG_DIR = "."
LOG_ARCHIVE_DIRNAME = ".log_archive"
LOG_FILENAME = ".log"
TIME_FORMAT = "%Y-%m-%d-%H:%M:%S"

# maximum size of newest logfile before it is move to the log archive
# archived log files will be slightly larger than this
MAX_LOG_FILE_SIZE_KiB = 1024
# maximum number of old logfiles to keep in the log archive
MAX_ARCHIVE_LOGS_COUNT = 50

log_file_lock: Lock = Lock()


def record(message: str, record_timestamp: bool = True) -> None:
    """Write a the provided text to the logfile.

    Args:
        message (str): the text to log
        record_timestamp (bool): whether or not a timestamp should be prepended
                            to the logged text
    """
    if not isinstance(message, str):
        message = str(message)
    log_file_path = os.path.join(LOG_DIR, LOG_FILENAME)
    log_file_lock.acquire()
    try:
        text = message
        if text[-1] != "\n":
            text = f"{message}\n"
        if record_timestamp:
            text = f"{time_stamp()} {text}"
        with open(log_file_path, "a+", encoding="utf-8") as f:
            f.write(text)
    except PermissionError:
        print(f"Logging: Permission denied: {os.path.abspath(log_file_path)}")

    # move log file to archive if it has become too big
    if os.stat(log_file_path).st_size >= MAX_LOG_FILE_SIZE_KiB * 1024:
        archive_dir = os.path.join(LOG_DIR, LOG_ARCHIVE_DIRNAME)
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        shutil.move(
            log_file_path,
            os.path.join(
                archive_dir,
                datetime.now().strftime("%Y-%m-%d-%H_%M_%S") + ".log",
            ),
        )

        # delete oldest log file if archive is too full
        archive_log_files = os.listdir(archive_dir)
        if len(archive_log_files) > MAX_ARCHIVE_LOGS_COUNT:
            archive_log_files.sort()
            oldest_log_file = archive_log_files[0]
            os.remove(os.path.join(archive_dir, oldest_log_file))
    log_file_lock.release()


# pylint: disable=unused-variable


def info(message: str) -> None:
    """Log a message with the INFO level."""
    if not isinstance(message, str):
        message = str(message)
    if PRINT_INFO:
        print(coloured(message, "green"))
    if RECORD_INFO:
        record("Info:      " + message)


def important(message: str) -> None:
    """Log a message with the IMPORTANT level."""
    if not isinstance(message, str):
        message = str(message)
    if PRINT_IMPORTANT:
        print(coloured(message, "blue"))
    if RECORD_IMPORTANT:
        record("Important: " + message)


def debug(message: str) -> None:
    """Log a message with the DEBUG level."""
    if not isinstance(message, str):
        message = str(message)
    if PRINT_DEBUG:
        print(coloured(message, "magenta"))
    if RECORD_DEBUG:
        record("Debug: " + message)


def warning(message: str) -> None:
    """Log a message with the WARNING level."""
    if not isinstance(message, str):
        message = str(message)
    if PRINT_WARNING:
        print(coloured(message, "yellow"))
    if RECORD_WARNING:
        record("Warning:   " + message)


def error(message: str) -> None:
    """Log a message with the ERROR level."""
    if not isinstance(message, str):
        message = str(message)
    traceback_data = None
    if LOG_ERROR_TRACEBACK:
        traceback_data = traceback.format_exc()
        if traceback_data == "NoneType: None\n":
            traceback_data = None
    if PRINT_ERROR:
        if traceback_data:
            print(coloured(traceback_data, "red"))
        print(coloured(message, "red"))
    if RECORD_ERROR:
        if traceback_data:
            record(traceback_data, record_timestamp=False)
        record("Error:     " + message)


def fatal(message: str) -> None:
    """Log a message with the ERROR level."""
    if not isinstance(message, str):
        message = str(message)
    traceback_data = None
    if LOG_FATAL_TRACEBACK:
        traceback_data = traceback.format_exc()
        if traceback_data == "NoneType: None\n":
            traceback_data = None
    if PRINT_FATAL:
        if traceback_data:
            print(coloured(traceback_data, "red"))
        print(coloured(message, "red"))
    if RECORD_FATAL:
        if traceback_data:
            record(traceback_data, record_timestamp=False)
        record("Fatal:     " + message)


def set_print_level(level: str) -> None:
    """Set which log severity level and above should be printed in the console.

    Args:
        level(str): values: "error", "warning", "important", "info"
    """
    level = level.lower()
    levels = ["error", "warning", "important", "info"]
    if level not in levels:
        raise ValueError(f"Argument must be one of the following: {levels}")
    # pylint: disable=global-statement
    global PRINT_INFO
    global PRINT_IMPORTANT
    global PRINT_WARNING
    global PRINT_ERROR

    PRINT_INFO = False
    PRINT_IMPORTANT = False
    PRINT_WARNING = False
    PRINT_ERROR = True
    if level == "error":
        return
    PRINT_WARNING = True
    if level == "warning":
        return
    PRINT_IMPORTANT = True
    if level == "important":
        return
    PRINT_INFO = True


def time_stamp() -> str:
    """Get a timestamp for the current local time."""
    return datetime.now().strftime(TIME_FORMAT)


def add_empty_line() -> None:
    """Add an empty line to the log file."""
    log_file_path = os.path.join(LOG_DIR, LOG_FILENAME)
    if (
        not os.path.exists(log_file_path)
        or os.stat(log_file_path).st_size == 0
    ):
        return
    with log_file_lock:
        with open(log_file_path, "a+", encoding="utf-8") as f:
            f.write("\n")
