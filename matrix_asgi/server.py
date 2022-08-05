#!/usr/bin/env python3
"""Matrix ASGI Server."""
import asyncio
import logging
from signal import SIGINT, SIGTERM
from typing import Any

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.exceptions import LocalProtocolError
from nio.responses import JoinError, RoomSendError
from nio.rooms import MatrixRoom

from markdown import markdown

from . import conf, utils

LOGGER = logging.getLogger("matrix-asgi.server")


class AsgiMatrixServer:
    """Matrix ASGI Server."""

    def __init__(self, /, application="", verbosity=0):
        """Initialize."""
        self.args = conf.get_parser(__doc__).parse_args()
        if verbosity:
            self.args.verbose = verbosity
        if application:
            self.args.application = application

        logging.basicConfig(level=50 - 10 * self.args.verbose)

        self.client = AsyncClient(self.args.matrix_url, self.args.matrix_id)
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.application = utils.get_application(self.args.application)

        self.app_scope = {
            "type": "matrix",
            "asgi": {
                "version": "3.0",
                "spec_version": "1.0",
            },
        }
        self.queue = None
        self.event = None

    def run(self):  # pragma: no cover
        """Start the synchronous ASGI server."""
        LOGGER.info("Starting...")
        asyncio.run(self.main())
        LOGGER.info("Stopped")

    async def login(self):
        """Login or re-login on matrix homeserver."""
        await self.client.login(self.args.matrix_pw)

    async def main(self, event=None):
        """Start the asynchronous ASGI server."""
        self.queue = asyncio.Queue()
        self.event = event or asyncio.Event()

        if event is None:  # pragma: no cover
            for sig in (SIGINT, SIGTERM):
                asyncio.get_running_loop().add_signal_handler(
                    sig, utils.terminate, self.event, sig
                )

        await self.login()
        asyncio.create_task(
            self.application(
                self.app_scope, receive=self.queue.get, send=self.app_send
            ),
        )
        asyncio.create_task(
            self.client.sync_forever(timeout=36_000),
        )
        await self.queue.put(
            {
                "type": "matrix.connect",
            }
        )

        LOGGER.info("Started")

        if event is None:  # pragma: no cover
            await self.serve()

    async def serve(self):
        """Server requests for ever."""
        await self.event.wait()
        await self.queue.put(
            {
                "type": "matrix.disconnect",
            }
        )
        LOGGER.info("Stopping...")
        await self.client.close()

    async def app_send(self, message):
        """ASGI application `send` method: Dispatch incomming Channel messages."""
        LOGGER.debug(f"app_send {message=}")
        assert message["type"] == "matrix.send"
        await self.matrix_room_send(message["room"], message["body"])

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        """Handle an incomming message from matrix-nio client: put it in the Queue."""
        LOGGER.debug("message_callback {room=} {event=}")
        await self.queue.put(
            {
                "type": "matrix.receive",
                "room": room.display_name,
                "user": room.user_name(event.sender),
                "body": event.body,
            }
        )

    async def join_room(self, room_id: str) -> bool:  # pragma: no cover
        """Use matrix-nio client to join a room."""
        LOGGER.debug(f"Join room {room_id=}")

        for _ in range(10):
            try:
                resp = await self.client.join(room_id)
                if not isinstance(resp, JoinError):
                    return True
                if resp.status_code == "M_UNKNOWN_TOKEN":
                    LOGGER.warning("Reconnecting")
                    await self.login()
                elif resp.status_code in ["M_FORBIDDEN", "M_CONSENT_NOT_GIVEN"]:
                    LOGGER.error("room access is forbidden")
                    return False
                elif resp.status_code == "M_UNKNOWN":
                    LOGGER.error(f"join error: {resp.transport_response.status}")
                    return False
            except LocalProtocolError as e:
                LOGGER.error(f"Send error: {e}")
            LOGGER.warning("Trying again")
        LOGGER.error("Homeserver not responding")
        return False

    async def send_room_message(self, room_id: str, content: dict[Any, Any]) -> bool:
        """Use matrix-nio client to send a Matrix message to a room."""
        LOGGER.debug(f"Sending room message in {room_id=}: {content=}")

        for _ in range(10):
            try:
                resp = await self.client.room_send(
                    room_id=room_id, message_type="m.room.message", content=content
                )
                if not isinstance(resp, RoomSendError):
                    return True
                if resp.status_code == "M_UNKNOWN_TOKEN":  # pragma: no cover
                    LOGGER.warning("Reconnecting")
                    await self.login()
                else:  # pragma: no cover
                    LOGGER.error(f"room send error {resp=}")
                    return False
            except LocalProtocolError as e:  # pragma: no cover
                LOGGER.error(f"Send error: {e}")
            LOGGER.warning("Trying again")  # pragma: no cover
        LOGGER.error("Homeserver not responding")  # pragma: no cover
        return False  # pragma: no cover

    async def matrix_room_send(self, room, message):
        """Handle an incoming matrix.send message from Channel: forward it to Matrix."""
        content = {
            "msgtype": "m.text",
            "body": message,
            "format": "org.matrix.custom.html",
            "formatted_body": markdown(message, extensions=["extra"]),
        }
        await self.send_room_message(room, content)
