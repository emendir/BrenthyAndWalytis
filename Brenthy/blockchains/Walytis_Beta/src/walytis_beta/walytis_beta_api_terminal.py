"""Machinery for handling WalytisAPI requests."""

# pylint: disable=import-error
from typing import Callable
import json
import os

from brenthy_tools_beta import log
from brenthy_tools_beta.utils import (
    bytes_to_string,
    from_b255_no_0s,
    string_to_bytes,
    string_to_time,
)
from brenthy_tools_beta.version_utils import decode_version, encode_version
from brenthy_tools_beta.utils import make_file_readable, make_directory_readable

from . import walytis_beta
from walytis_beta_tools.block_model import short_from_long_id
from walytis_beta_tools.versions import (
    WALYTIS_BETA_API_PROTOCOL_VERSION,
    WALYTIS_BETA_CORE_VERSION,
)
from walytis_beta_tools.exceptions import (
    BLOCK_NOT_FOUND,
    BLOCKCHAIN_EXISTS_MESSAGE,
    NO_SUCH_BLOCKCHAIN_MESSAGE,
    NO_SUCH_INVITATION_MESSAGE,
    WALYTIS_BETA_ERROR_MESSAGE,
)


def list_blockchains() -> bytes:
    """Get a list of running blockchains."""
    return json.dumps(
        [
            (blockchain.blockchain_id, blockchain.name)
            for blockchain in walytis_beta.blockchains
        ]
    ).encode()


def create_blockchain(payload: bytearray) -> bytes:
    """Create and runs a new blockchain with the given name."""
    data = json.loads(payload.decode())
    blockchain_name = data["blockchain_name"]
    if blockchain_name and [
        bc
        for bc in walytis_beta.blockchains
        if blockchain_name in (bc.name, bc.blockchain_id)
    ]:
        return json.dumps(
            {
                "success": False,
                "error": BLOCKCHAIN_EXISTS_MESSAGE,
                "blockchain_name": blockchain_name,
                "blockchain_id": None,
            }
        ).encode()

    blockchain = walytis_beta.create_blockchain(blockchain_name)
    return json.dumps(
        {
            "success": bool(blockchain),
            "blockchain_id": blockchain.blockchain_id,
        }
    ).encode()


def delete_blockchain(payload: bytearray) -> bytes:
    """Delete the blockchain with the given name or id."""
    blockchain_id = payload.decode()
    if not [
        bc
        for bc in walytis_beta.blockchains
        if blockchain_id in (bc.name, bc.blockchain_id)
    ]:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": blockchain_id,
            }
        ).encode()

    result = walytis_beta.delete_blockchain(blockchain_id)
    return json.dumps({"success": bool(result)}).encode()


def create_block(payload: bytearray) -> bytes:
    """Ask the blockcahin to create and publish a new block."""
    try:
        blockchain = walytis_beta.get_blockchain(
            payload[: payload.index(bytearray([0]))].decode()
        )
        if not blockchain:
            return json.dumps(
                {"success": False, "error": NO_SUCH_BLOCKCHAIN_MESSAGE}
            ).encode()
        payload = payload[payload.index(bytearray([0])) + 1:]
        n_topics_bytes = payload[: payload.index(bytearray([0]))]
        # decode the array of bytes that encode the number of topic IDs
        # included in this block
        n_topics = from_b255_no_0s(n_topics_bytes)
        # remove the topic number and the follwing 0 from the start of payload.
        # + 1 to remove the 0 separator as well
        payload = payload[len(n_topics_bytes) + 1:]

        topics = []

        i = 0
        while i < n_topics:
            topic = payload[: payload.index(bytearray([0, 0, 0]))]
            # removing the collected topic part, including the following 0,
            # from payload
            payload = payload[payload.index(bytearray([0, 0, 0])) + 3:]

            # adding the topic to the correct topic block list
            # adding this topic to this blocks list of topics
            topics.append(topic.decode())
            i = i + 1

        content = payload
        # print("AppCom: ", topics)
        block = blockchain.create_block(content, topics)
        return json.dumps(
            {"success": True, "block_id": bytes_to_string(block.short_id)}
        ).encode()

    except Exception as e:
        log.error("Failed to build block:\n" + str(e))
        return json.dumps(
            {"success": False, "error": WALYTIS_BETA_ERROR_MESSAGE}
        ).encode()


def get_block(payload: bytearray) -> bytes:
    """Get a block object from a blokchain given its block ID."""
    try:
        data = json.loads(payload.decode())
        blockchain_id = data["blockchain_id"]
        block_id = string_to_bytes(data["block_id"])
        blockchain = walytis_beta.get_blockchain(blockchain_id)
        if not blockchain:
            return json.dumps(
                {"success": False, "error": NO_SUCH_BLOCKCHAIN_MESSAGE}
            ).encode()
        if blockchain.is_block_known(block_id):
            return json.dumps(
                {"success": True, "block_id": bytes_to_string(block_id)}
            ).encode()

        block = blockchain.download_and_process_block(block_id)
        if block:
            return json.dumps(
                {"success": True, "block_id": bytes_to_string(block.short_id)}
            ).encode()

        else:
            return json.dumps(
                {"success": False, "error": BLOCK_NOT_FOUND}
            ).encode()
    except Exception as e:
        log.error("Failed to build block:\n" + str(e))
        return json.dumps(
            {"success": False, "error": WALYTIS_BETA_ERROR_MESSAGE}
        ).encode()


def is_block_known(payload: bytearray) -> bytes:
    """Check if the given block is known."""
    try:
        blockchain = walytis_beta.get_blockchain(
            payload[: payload.index(bytearray([0]))].decode()
        )
        if not blockchain:
            return json.dumps(
                {"success": False, "error": NO_SUCH_BLOCKCHAIN_MESSAGE}
            ).encode()
        short_id = payload[payload.index(bytearray([0])) + 1:]
        result = blockchain.is_block_known(short_id)
        return json.dumps(
            {
                "blockchain_name": blockchain.name,
                "blockchain_id": blockchain.blockchain_id,
                "is known": result,
            }
        ).encode()
    except Exception as e:
        log.error("Failed to subscribe to topic:\n" + str(e))

        return json.dumps(
            {"success": False, "error": WALYTIS_BETA_ERROR_MESSAGE}
        ).encode()


def get_latest_blocks(payload: bytearray) -> bytes:
    """Get the latest few blocks from the block records.

    The order of the returned blocks is from most recent to oldest.
    """
    try:
        data = json.loads(payload.decode())
        blockchain = walytis_beta.get_blockchain(data["blockchain_id"])
        if not blockchain:
            return json.dumps(
                {
                    "success": False,
                    "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                    "blockchain_id": blockchain.blockchain_id,
                }
            ).encode()
        block_id = data.get("block short_id")
        amount, since_date, topics, long_ids = (
            data.get("amount"),
            data.get("since_date"),
            data.get("topics"),
            data.get("long_ids"),
        )

        # long_ids is False by default for backwards-compatibility
        if long_ids is None:
            long_ids = False

        if since_date:
            since_date = string_to_time(since_date)
        else:
            since_date = None
        block_ids = blockchain.load_latest_block_ids(
            amount, since_date, topics
        )
        # print("AppCom: Got latest blocks")
        if long_ids:
            block_ids_encoded = [
                bytes_to_string(block_id) for block_id in block_ids
            ]
        else:
            block_ids_encoded = [
                bytes_to_string(short_from_long_id(block_id))
                for block_id in block_ids
            ]

        return json.dumps(
            {
                "success": True,
                "blockchain_name": blockchain.name,
                "blockchain_id": blockchain.blockchain_id,
                "block_ids": block_ids_encoded,
            }
        ).encode()
    except Exception as e:
        log.error("Failed to subscribe to topic:\n" + str(e))
        return json.dumps(
            {"success": False, "error": WALYTIS_BETA_ERROR_MESSAGE}
        ).encode()


def get_blockchain_data(payload: bytearray) -> bytes:
    """Create a zip file of a blockchain's data, returning its path."""
    blockchain = walytis_beta.get_blockchain(payload.decode())
    if not blockchain:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": payload.decode(),
            }
        ).encode()
    result = blockchain.zip_appdata()
    make_file_readable(result)
    make_directory_readable(os.path.dirname(result))

    return json.dumps(
        {
            "success": True,
            "blockchain_name": blockchain.name,
            "blockchain_id": blockchain.blockchain_id,
            "path": result,
        }
    ).encode()


def get_peers(payload: bytearray) -> bytes:
    """
    Returns a list of known peers in order of most recently contacted first.
    """
    blockchain = walytis_beta.get_blockchain(payload.decode())
    if not blockchain:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": payload.decode(),
            }
        ).encode()
    result = blockchain.get_peers()
    return json.dumps(
        {
            "success": True,
            "blockchain_name": blockchain.name,
            "blockchain_id": blockchain.blockchain_id,
            "peers": result,
        }
    ).encode()


def get_invitations(payload: bytearray) -> bytes:
    """
    Get the list of currently active invitations for the specified blockchain.
    """
    blockchain = walytis_beta.get_blockchain(payload.decode())
    if blockchain:
        return json.dumps(
            {"success": True, "invitations": blockchain.invitations}
        ).encode()
    else:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": payload.decode(),
            }
        ).encode()


def create_invitation(payload: bytearray) -> bytes:
    """
    Create a code which another computer can use to join this blockchain.
    """

    data = json.loads(payload.decode())
    blockchain = walytis_beta.get_blockchain(data["blockchain_id"])
    if not blockchain:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": data["blockchain_id"],
            }
        ).encode()
    result = blockchain.create_invitation(
        one_time=data["one_time"], shared=data["shared"]
    )

    return json.dumps({"success": True, "invitation": result}).encode()


def delete_invitation(payload: bytearray) -> bytes:
    """
    Delete a invitation from the blockchain.
    """

    data = json.loads(payload.decode())
    blockchain = walytis_beta.get_blockchain(data["blockchain_id"])
    if not blockchain:
        return json.dumps(
            {
                "success": False,
                "error": NO_SUCH_BLOCKCHAIN_MESSAGE,
                "blockchain_id": data.decode(),
            }
        ).encode()
    result = blockchain.delete_invitation(data["invitation"])
    if result:
        return json.dumps({"success": True}).encode()
    else:
        return json.dumps(
            {"success": result, "error": NO_SUCH_INVITATION_MESSAGE}
        ).encode()


def join_blockchain_from_cid(payload: bytearray) -> bytes:
    """Join an existing live blockchain, given the IPFS CID of its data."""
    data = json.loads(payload.decode())
    blockchain = walytis_beta.join_blockchain_from_cid(
        data["blockchain_id"],
        data["blockchain_data_cid"],
        blockchain_name=data["blockchain_name"],
    )
    if not blockchain:
        return json.dumps({"success": False}).encode()
    return json.dumps(
        {"success": True, "blockchain_id": blockchain.blockchain_id}
    ).encode()


def join_blockchain(payload: bytearray) -> bytes:
    """Join an existing live blockchain, given a zip file of its data."""
    data = json.loads(payload.decode())
    invitation = data["invitation"]
    blockchain_name = data["blockchain_name"]
    blockchain_id = invitation["blockchain_id"]
    if blockchain_id in walytis_beta.get_blockchain_ids():
        return json.dumps(
            {
                "success": False,
                "error": BLOCKCHAIN_EXISTS_MESSAGE,
                "blockchain_id": blockchain_id,
            }
        ).encode()
    if blockchain_name in walytis_beta.get_blockchain_names():
        return json.dumps(
            {
                "success": False,
                "error": BLOCKCHAIN_EXISTS_MESSAGE,
                "blockchain_name": blockchain_name,
            }
        ).encode()
    blockchain = walytis_beta.join_blockchain(
        invitation, blockchain_name=blockchain_name
    )
    if blockchain:
        return json.dumps(
            {"success": True, "blockchain_id": blockchain.blockchain_id}
        ).encode()
    else:
        return json.dumps({"success": False}).encode()


def get_walytis_beta_version() -> bytes:
    """Get the Walytis_Beta node version"""
    return json.dumps(
        {"walytis_beta_core_version": WALYTIS_BETA_CORE_VERSION}
    ).encode()



def request_router(request: bytearray) -> bytes:
    """
    This function processes all requests incoming from the apps,
    relaying them to the correct specialised task-specific handlers.
    """
    try:
        function = request[: request.index(bytearray([0]))].decode()
        payload = request[request.index(bytearray([0])) + 1:]
        if function == "list_blockchains":
            return list_blockchains()
        elif function == "create_block":
            return create_block(payload)
        elif function == "get_block":
            return get_block(payload)
        elif function == "is_block_known":
            return is_block_known(payload)
        elif function == "get_latest_blocks":
            return get_latest_blocks(payload)
        elif function == "get_blockchain_data":
            return get_blockchain_data(payload)
        elif function == "get_peers":
            return get_peers(payload)
        elif function == "get_invitations":
            return get_invitations(payload)
        elif function == "create_invitation":
            return create_invitation(payload)
        elif function == "delete_invitation":
            return delete_invitation(payload)
        elif function == "join_blockchain_from_cid":
            return join_blockchain_from_cid(payload)
        elif function == "join_blockchain":
            return join_blockchain(payload)
        elif function == "create_blockchain":
            return create_blockchain(payload)
        elif function == "delete_blockchain":
            return delete_blockchain(payload)
        if function == "get_walytis_beta_version":
            return get_walytis_beta_version()

        else:
            log.warning(
                "walytis_beta_api_terminal: Received request that was not "
                f"understood: {function} {payload}"
            )
            return json.dumps(
                {"success": False, "error": "not understood"}
            ).encode()
    except Exception as e:
        log.error(
            "Unhandled Exception in walytis_beta_api_terminal.request_router:"
            f"\n{e}"
        )
        return json.dumps(
            {"success": False, "error": WALYTIS_BETA_ERROR_MESSAGE}
        ).encode()


def api_request_handler(request: bytearray) -> bytearray:
    """Handle incoming WalytisAPI requests."""
    walytis_beta_api_version = decode_version(
        request[: request.index(bytearray([0]))]
    )
    payload = request[request.index(bytearray([0])) + 1:]
    reply = request_router(payload)
    return (
        encode_version(WALYTIS_BETA_API_PROTOCOL_VERSION)
        + bytearray([0])
        + reply
    )


_publish_event_handlers: list[Callable[[dict, list[str]], None]] = []


def add_eventhandler(eventhandler: Callable[[dict, list[str]], None]):
    _publish_event_handlers.append(eventhandler)


def publish_event(
    blockchain_id: str, message: dict, topics: list[str] | str | None = None
) -> None:
    """Publish a blockchain's message to all subscribed applications."""
    if not topics:
        topics = []
    if isinstance(topics, str):
        topics = [topics]
    if "" not in topics:
        topics.append("")
    for eventhandler in _publish_event_handlers:
        eventhandler(
            message,
            [f"{blockchain_id}-{topic}" for topic in topics],
        )
