import sys
import os
WORKDIR=os.path.dirname(os.path.abspath(__file__))
sys.path.append(WORKDIR)
WALYTIS_SRC_DIR=os.path.join(WORKDIR, "src")

# ensure all walytis modules are loaded from this source code, not any other package installations
sys.path.insert(0, WALYTIS_SRC_DIR)

from src.walytis_beta import run_blockchains, terminate, add_eventhandler, set_appdata_dir, api_request_handler, get_walytis_appdata_dir, version