import os
from ipfs_tk_generics import IpfsClient
from brenthy_tools_beta import log

# initialise IPFS
USE_IPFS_NODE = os.environ.get("USE_IPFS_NODE", "").lower() in ["true", "1"]
IPFS_REPO_DIR = os.environ.get("IPFS_REPO_DIR", "")
ipfs:IpfsClient
if USE_IPFS_NODE:
    if IPFS_REPO_DIR:
        if not os.path.exists(IPFS_REPO_DIR):
            raise Exception(
                "The path specified in the environment variable IPFS_REPO_DIR "
                f"doesn't exist: {IPFS_REPO_DIR}"
            )
    else:
        IPFS_REPO_DIR = os.path.abspath(os.path.join(".ipfs_repo"))
        if not os.path.exists(IPFS_REPO_DIR):
            os.makedirs(IPFS_REPO_DIR)
        os.environ["IPFS_REPO_DIR"]=IPFS_REPO_DIR
    print(f"IPFS repo: {IPFS_REPO_DIR}")
    from ipfs_node import IpfsNode

    ipfs = IpfsNode(IPFS_REPO_DIR)
else:
    from ipfs_remote import IpfsRemote
    ipfs = IpfsRemote("localhost:5001")
    try:
        ipfs.wait_till_ipfs_is_running(timeout_sec=5)
    except TimeoutError:
        log.warning("IPFS isn't running. Waiting for IPFS to start...")
        ipfs.wait_till_ipfs_is_running()
        log.warning("IPFS running now.")