"""The library for interacting with Walytis.

This package contains the blockchain-application developer's API for
interacting with Walytis, as well as utilities common to both Walytis and
`wlaytis_beta_api`.
"""
import os
# os.environ["USE_IPFS_NODE"] = "true"
os.environ["WALYTIS_BETA_API_TYPE"] = "WALYTIS_BETA_DIRECT_API"
os.environ["AUTO_LOAD_BAP_MODULES"] = "false"

from ._walytis_beta.walytis_beta_api import (
    list_blockchains,
    list_blockchain_names,
    list_blockchain_ids,
    get_blockchain_id,
    get_blockchain_name,
    create_blockchain,
    delete_blockchain,
    join_blockchain,
    join_blockchain_from_zip,
    join_blockchain_from_cid,
    create_block,
    get_block,
    is_block_known,
    get_latest_blocks,
    get_blockchain_data,
    create_invitation,
    get_invitations,
    delete_invitation,
    get_walytis_beta_version,
    get_walytis_beta_version_string,
    get_walytis_beta_api_version,
    get_walytis_beta_api_version_string,
    BlocksListener,
    get_and_read_block,
    read_block,
    Blockchain,
    Block,
    decode_short_id,
    decode_long_id,
    short_from_long_id,
)
from ._walytis_beta import (
    set_appdata_dir,
    run_blockchains,
    terminate
)


from ._walytis_beta.walytis_beta_tools.exceptions import (
    WalytisReplyDecodeError,
    WalytisBugError,
    NoSuchBlockchainError,
    BlockchainAlreadyExistsError,
    NoSuchInvitationError,
    JoinFailureError,
    BlockNotFoundError,
    BlockCreationError,
    BlockIntegrityError,
)
from ._walytis_beta.walytis_beta_tools.versions import (
    WALYTIS_BETA_PROTOCOL_VERSION,
    WALYTIS_BETA_API_PROTOCOL_VERSION,
    WALYTIS_BETA_API_VERSION,
    WALYTIS_BETA_CORE_VERSION,
)

from ._walytis_beta.walytis_beta_tools._experimental.config import ipfs
