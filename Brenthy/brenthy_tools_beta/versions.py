"""The versions of the the various Brenthy components."""

# pylint: disable=unused-variable

# the newest version of the communication protocol used by the Brenthy node and
# the brenthy_tools_beta library to communicate with each other
BRENTHY_API_PROTOCOL_VERSION = 4

# the version of the core Brenthy software which runs blockchains
BRENTHY_CORE_VERSION = (
    BRENTHY_API_PROTOCOL_VERSION,  # major: the BrenthyAPI Protocol version
    1,  # minor: significant changes to Brenthy since the last major update
    4,  # patch: minor changes to Brenthy since the last minor update
)


# the version of the brenthy_api library which is used by applications
# to communicate with Brenthy Core to interact with blockchains
BRENTHY_TOOLS_VERSION = (
    BRENTHY_API_PROTOCOL_VERSION,  # major: the BrenthyAPI Protocol version
    0,  # minor: changes to brenthy_api but not BAP since the last major update
    3,  # patch: changes outside brenthy_api since the last minor update
)
