"""Walytis_Beta: a nonlinear blockchain type."""

# exposing the Walytis_Beta  in the way that Brenthy can find it
# pylint: disable=unused-variable
from .networking import ipfs
from .walytis_beta import Blockchain
from .walytis_beta import run_blockchains, terminate
from walytis_beta_tools.versions import WALYTIS_BETA_CORE_VERSION as version
from .walytis_beta_api_terminal import api_request_handler, add_eventhandler
from .walytis_beta_appdata import set_appdata_dir, get_walytis_appdata_dir
from brenthy_tools_beta import log
