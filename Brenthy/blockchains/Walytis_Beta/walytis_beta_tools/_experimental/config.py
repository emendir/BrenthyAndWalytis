import os
from ipfs_tk_generics import IpfsClient

ipfs_node:IpfsClient

USE_IPFS_NODE = os.environ.get("USE_IPFS_NODE", "").lower() in ["true", "1"]
IPFS_REPO_DIR = os.environ.get("IPFS_REPO_DIR", "")
from brenthy_tools_beta import log
if USE_IPFS_NODE:
    from ipfs_node import IpfsNode
    if not IPFS_REPO_DIR:
        print("WARNING - IPFS EPHEMERAL NODE: walytis_beta_api is creating and ephemeral IPFS node.")
    ipfs = IpfsNode(IPFS_REPO_DIR)
else:
    from ipfs_remote import IpfsRemote
    ipfs = IpfsRemote("127.0.0.1:5001")
    try:
        ipfs.wait_till_ipfs_is_running(timeout_sec=5)
    except TimeoutError:
        log.warning("IPFS isn't running. Waiting for IPFS to start...")
        ipfs.wait_till_ipfs_is_running()
        log.warning("IPFS running now, starting Brenthy now...")