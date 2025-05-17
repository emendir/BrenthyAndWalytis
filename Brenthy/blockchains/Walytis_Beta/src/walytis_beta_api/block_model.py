"""DEPRECATING: The fundamental machinery constituting Blocks."""

import hashlib
from copy import deepcopy

# from random import seed
# from random import randint
from datetime import datetime
from secrets import randbits

from brenthy_tools_beta import log
from brenthy_tools_beta.utils import (  # pylint: disable=unused-import
    bytes_from_b255_no_0s,
    bytes_to_b255_no_0s,
    decode_timestamp,
    encode_timestamp,
    from_b255_no_0s,
    to_b255_no_0s,
)
from brenthy_tools_beta.version_utils import decode_version, encode_version

from .exceptions import BlockIntegrityError, InvalidBlockIdError
from walytis_beta_tools._experimental.generic_block import _GenericBlockImpl as GenericBlock

PREFERRED_HASH_ALGORITHM = "sha512"

from walytis_beta_tools.block_model import (
    Block,
    decode_short_id,
    decode_long_id,
    short_from_long_id,
)
print("DEPRECATING: import from walytis_beta_api instead of walytis_beta_api.block_model")