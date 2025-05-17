"""The versions of the the various Walytis components."""

# the newest version of the Walytis_Beta protocol, which defines
# how nodes communicate and how block IDs and block-files are structured
WALYTIS_BETA_PROTOCOL_VERSION = 2

# the newest version of the communication protocol used by the Walytis node
# and the walytis_beta_api library to communicate with each other
WALYTIS_BETA_API_PROTOCOL_VERSION = (WALYTIS_BETA_PROTOCOL_VERSION, 4)

# the version of the walytis_api library which is used by applications
# to communicate with the Walytis_Beta node to interact with blockchains
WALYTIS_BETA_API_VERSION = (*WALYTIS_BETA_API_PROTOCOL_VERSION, 6)

# the version of the Walytis core software, which runs blockchains
WALYTIS_BETA_CORE_VERSION = (*WALYTIS_BETA_API_PROTOCOL_VERSION, 7)

_WALYTIS_BETA_API_VERSION=".".join([str(v) for v in WALYTIS_BETA_API_VERSION])
