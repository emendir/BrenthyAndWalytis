"""Test Brenthy's logging system."""

import os
import shutil
import sys
import tempfile
import time

from testing_utils import mark

if True:
    brenthy_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Brenthy"
    )
    sys.path.insert(0, brenthy_dir)
    from brenthy_tools_beta import log

tempdir: str


def test_preparations() -> None:
    """Get everything needed to run the tests ready."""
    global tempdir
    tempdir = tempfile.mkdtemp()
    log.LOG_DIR = tempdir
    log.MAX_LOG_FILE_SIZE_KiB = 10
    log.MAX_ARCHIVE_LOGS_COUNT = 5
    log.LOG_ARCHIVE_DIRNAME = "test_log_archive"
    log.LOG_FILENAME = "test.log"


logfile_path: str = ""
oldest_log_file_path: str = ""


def test_log_archiving() -> None:
    """Test that logs get archived when getting too large."""
    global oldest_log_file_path
    global logfile_path
    logfile_path = os.path.join(log.LOG_DIR, log.LOG_FILENAME)

    size_exceeded = False
    for i in range(20):
        log.info("testing " * 100)
        if os.path.exists(logfile_path):
            if (
                os.path.getsize(logfile_path)
                > log.MAX_LOG_FILE_SIZE_KiB * 1024
            ):
                size_exceeded = True
    print(mark(not size_exceeded), "Main log file's size stays within bounds.")
    oldest_log_files = os.listdir(
        os.path.join(tempdir, log.LOG_ARCHIVE_DIRNAME)
    )
    print(mark(len(oldest_log_files) == 1), ("Old logs archived."))
    oldest_log_file = oldest_log_files[0]
    oldest_log_file_path = os.path.join(
        tempdir, log.LOG_ARCHIVE_DIRNAME, oldest_log_file
    )


def test_old_log_file_size() -> None:
    """Test that ."""
    file_size = os.path.getsize(oldest_log_file_path)
    min_size = log.MAX_LOG_FILE_SIZE_KiB * 1024  # Maximum size in bytes
    max_size = int(1.1 * min_size)  # Minimum size in bytes

    archived_log_size_exceeded = False
    main_log_size_exceeded = False
    if not min_size <= file_size <= max_size:
        archived_log_size_exceeded = True
    else:
        for i in range(80):
            log.info("testing " * 100)
            # slow down so that archived logs don't overwrite each other
            time.sleep(0.2)
            if os.path.exists(logfile_path):
                file_size = os.path.getsize(logfile_path)
                if not file_size < log.MAX_LOG_FILE_SIZE_KiB * 1024:
                    main_log_size_exceeded = True
                    break
        for old_file_name in os.listdir(
            os.path.join(tempdir, log.LOG_ARCHIVE_DIRNAME)
        ):
            old_file_path = os.path.join(
                tempdir, log.LOG_ARCHIVE_DIRNAME, old_file_name
            )
            file_size = os.path.getsize(old_file_path)
            if not min_size <= file_size <= max_size:
                archived_log_size_exceeded = True
                break
    print(
        mark(not main_log_size_exceeded),
        "Main log file's size stays within bounds.",
    )
    print(
        mark(not archived_log_size_exceeded),
        "Archived log file sizes within bounds.",
    )


def test_old_log_deletion() -> None:
    """Test that ."""
    print(
        mark(not os.path.exists(oldest_log_file_path)),
        "Oldest log file deleted.",
    )

    shutil.rmtree(tempdir)


def run_tests() -> None:
    """Run all tests."""
    print("\nRunning tests for logging...")
    test_preparations()

    test_log_archiving()
    test_old_log_file_size()
    test_old_log_deletion()


if __name__ == "__main__":
    run_tests()
