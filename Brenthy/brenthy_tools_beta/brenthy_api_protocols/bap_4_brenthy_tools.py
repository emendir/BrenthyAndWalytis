"""Brenthy API Protocol version 1, on Brenthy-Tool's side.

This module contains the machinery used by brenthy_tools.brenthy_api for
BrenthyAPI communication with Brenthy Core, using the version 1 BrenthyAPI
Protocol.
This module's counterpart, which contain's Brenthy Core's machinery, is at
../../api_terminal/brenthy_api_protocols/bap_4_brenthy_core.py
"""

import json
from inspect import signature
from threading import Thread
from types import FunctionType

import zmq
from brenthy_tools_beta import bt_endpoints, log
from brenthy_tools_beta.brenthy_api_addresses import (
    BRENTHY_IP_ADDRESS, BAP_4_RPC_PORT, BAP_4_PUB_PORT
)
from brenthy_tools_beta.bt_endpoints import (
    CantConnectToSocketError,
    send_request_zmq,
)
from brenthy_tools_beta.utils import function_name

BAP_VERSION = 4  # pylint: disable=unused-variable

# keep track of contexts to avoid problems caused by garbage collector
CONTEXTS = []


def send_request(request: bytearray | bytes) -> bytes:  # pylint: disable=unused-variable
    """Send a BrenthyAPI request to Brenthy-Core, returning its reply.

    Args:
        request (bytearray): the data to send to Brenthy-Core
    Returns:
        bytearray: the response received from Brenthy-Core
    """
    # try send_request_zmq, as it is faster
    return send_request_zmq(request, (BRENTHY_IP_ADDRESS, BAP_4_RPC_PORT))


class EventListener(bt_endpoints.EventListener):  # pylint: disable=unused-variable
    """Object for listening to events published by Brenthy Core.

    Asks the Brenthy API Terminal to notify us when a certain blockchain type
    publishes events, optionally only events from the specified set of topics,
    calling the provided eventhandler function when such a topic is received.

    Examples of eventhandlers:
    ```python
    def _on_new_block_received(data: dict):
       pass

    def _on_new_block_received(data: dict, topic:str):
       pass
    ```
    """

    def __init__(
        self,
        eventhandler: FunctionType,
        topics: (list[str] | str | None) = None,
    ):
        """Listen for events from Brenthy Core.

        Args:
            eventhandler (FuncType): a function that takes as input a
                dict (event-data) and optionally a string (topic)
                See class docstring for examples.
            topics (list[str] | str): the topics to filter messages by
        """
        self._terminate = False
        try:
            self.zmq_context = zmq.Context()
            CONTEXTS.append(self.zmq_context)
        except:
            raise CantConnectToSocketError(protocol="ZMQ") from None
        if not topics:
            topics = []
        if isinstance(topics, str):
            topics = [topics]
        if not isinstance(topics, list):
            error_message = (
                f"BrenthyAPI: EventListener("
                f"{topics}): Parameter topics must be of type list or str, "
                f"not {type(topics)}"
            )
            log.error(error_message)
            raise ValueError(error_message)
        self.eventhandler = eventhandler
        self.topics = topics
        n_params = len(signature(self.eventhandler).parameters)
        if n_params == 0:
            error_message = (
                f"BAP-4-BT.EventListener {topics}: "
                "eventhandler must have 1 or 2 parameters: (data, topic)"
            )
            log.error(f"BrenthyAPI: {function_name()}: {error_message}")
            raise TypeError(error_message)

        # if no topic
        if not self.topics:
            self.topics = [""]

        self.listener_thread = Thread(
            target=self._listen, args=(), name="BrenthyAPI-ListenToEvents"
        )
        self.listener_thread.start()

    def _listen(self) -> None:
        """Listen for messages and call user's eventhandler when received."""
        self.socket = self.zmq_context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, 1)
        # Connects to a bound self.socket
        self.socket.connect(
            f"tcp://{BRENTHY_IP_ADDRESS}:{BAP_4_PUB_PORT}"
        )
        for topic in self.topics:
            self.socket.subscribe(json.dumps({"topic": topic})[:-1] + ",")

            log.info(
                "BAP-4-BT.EventListener.listen: "
                + str(json.dumps({"topic": topic})[:-1] + ", ")
            )
        try:
            poller = zmq.Poller()
            poller.register(self.socket, zmq.POLLIN)
            while True:
                if self._terminate:
                    break
                events = dict(poller.poll(1000))
                if events:
                    if events.get(self.socket) == zmq.POLLIN:
                        data = json.loads(
                            self.socket.recv_string(flags=zmq.NOBLOCK)
                        )
                        topic = data["topic"]
                        data.pop("topic")  # remove topic from data
                        if self._terminate:
                            break

                        # extract the topic which the blockchain's api_terminal
                        # provided to the brenthy api_terminal

                        # call the eventhandler, passing it the data and topic
                        n_params = len(signature(self.eventhandler).parameters)
                        params: tuple
                        if n_params == 1:
                            params = (data,)
                        else:
                            params = (data, topic)
                        # log.info(
                        #     "BAP-4-BT.EventListener.listen: passing on "
                        #     f"received block to eventhandler with {n_params} "
                        #     f"parameters for topic {topic}"
                        # )

                        Thread(
                            target=self.eventhandler,
                            args=params,
                            name="EventListener.eventhandler",
                        ).start()
        except Exception as e:  # pylint:disable=broad-exception-caught
            log.error(f"BrenthyAPI.EventListener.listen: {e}")

        # clean up resources
        self.socket.close()
        self.zmq_context.term()

    def terminate(self) -> None:
        """Stop listening for events and clean up resources."""
        self._terminate = True

    def __del__(self):
        """Stop listening for events and clean up resources."""
        self.terminate()
