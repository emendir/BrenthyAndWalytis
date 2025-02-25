"""The network addresses via which Brenthy uses for BrenthyAPI."""
import os
# pylint: disable=unused-variable
DEF_BRENTHY_IP_ADDRESS = "127.94.21.1"
DEF_BRENTHY_API_IP_LISTEN_ADDRESS = DEF_BRENTHY_IP_ADDRESS
# edit BRENTHY_IP_ADDRESS if user set an environment variable
BRENTHY_IP_ADDRESS = os.environ.get(
    "BRENTHY_IP_ADDRESS",
     DEF_BRENTHY_IP_ADDRESS
)
BRENTHY_API_IP_LISTEN_ADDRESS = os.environ.get(
    "BRENTHY_API_IP_LISTEN_ADDRESS",
     DEF_BRENTHY_API_IP_LISTEN_ADDRESS
)

BAP_3_RPC_PORT = 29200
BAP_4_RPC_PORT = 29201
BAP_4_PUB_PORT = 29202
