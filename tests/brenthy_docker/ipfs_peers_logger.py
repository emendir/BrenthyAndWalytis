import time
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, UTC
from ipfs_remote import IpfsRemote
import os
from emtest.log_utils import get_app_log_dir

LOG_TIMESTAMP_FORMAT = "%Y-%m-%d~%H:%M:%S.%f"

LOG_PATH = os.path.join(
    get_app_log_dir("IpfsPeersLogger", "Waly"), "ipfs_peers_logger.log"
)


class MicrosecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)

        result = dt.strftime(datefmt)

        # convert microseconds to milliseconds
        if datefmt[-2:] == "%f":
            result = result[:-3]

        return result


formatter = MicrosecondFormatter(
    "%(asctime)s [%(levelname)s] %(name)s | %(message)s",
    datefmt=LOG_TIMESTAMP_FORMAT,
)
formatter_peers = MicrosecondFormatter(
    "%(asctime)s | %(message)s",
    datefmt=LOG_TIMESTAMP_FORMAT,
)
file_handler = TimedRotatingFileHandler(
    LOG_PATH,
    when="D",  # rotate daily
    interval=1,
    backupCount=2,  # keep logs for 30 days
)
file_handler.setFormatter(formatter_peers)

peers_logger = logging.getLogger("ipfs_peer_monitor")
peers_logger.setLevel(logging.INFO)
peers_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)


def main():
    ipfs = IpfsRemote()

    # peer_id -> connection_start_time (datetime)
    active_connections = {}

    logger.info("Starting IPFS peer monitor.")

    while True:
        try:
            current_peers = set(ipfs.peers.list_peers())
        except Exception as e:
            logger.error(f"Failed to fetch peers: {e}")
            time.sleep(1)
            continue

        # Detect new peers
        for peer in current_peers:
            if peer not in active_connections:
                active_connections[peer] = datetime.now(UTC)
                peers_logger.info(f"Peer appeared: {peer}")

        # Detect removed peers
        removed = [
            peer for peer in active_connections if peer not in current_peers
        ]

        for peer in removed:
            start_time = active_connections.pop(peer)
            end_time = datetime.now(UTC)
            duration = (end_time - start_time).total_seconds()

            # peers_logger.info(f"{start_time.isoformat()}Z {duration} {peer}")
            peers_logger.info(f"Peer left:     {peer}")

        time.sleep(1)


if __name__ == "__main__":
    main()
