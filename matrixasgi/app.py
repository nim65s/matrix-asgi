#!/usr/bin/env python3
"""Matrix ASGI Server."""
import asyncio
import importlib
import logging
from signal import SIGINT, SIGTERM
import sys
from typing import Dict, Any

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.exceptions import LocalProtocolError
from nio.responses import JoinError, RoomSendError
from nio.rooms import MatrixRoom

from markdown import markdown

from . import conf

LOGGER = logging.getLogger("matrixasgi")


class Server:
    def __init__(self):
        self.args = conf.get_parser().parse_args(__doc__)

        logging.basicConfig(level=50 - 10 * self.args.verbose)

        self.client = AsyncClient(self.args.matrix_url, self.args.matrix_id)
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.application = get_application(self.args.application)

        self.app_scope = {
            "type": "matrix",
            "asgi": {
                "version": "3.0",
                "spec_version": "1.0",
            },
        }
        self.queue = None

    def run(self):
        LOGGER.info("Starting...")
        asyncio.run(self.main())
        LOGGER.info("Stopped")

    def terminate(self, event, signal):
        """Close handling stuff."""
        event.set()
        asyncio.get_running_loop().remove_signal_handler(signal)

    async def main(self):
        self.queue = asyncio.Queue()
        self.event = asyncio.Event()

        for sig in (SIGINT, SIGTERM):
            asyncio.get_running_loop().add_signal_handler(
                sig, self.terminate, self.event, sig
            )

        await self.client.login(self.args.matrix_pw)
        asyncio.create_task(
            self.application(
                self.app_scope, receive=self.app_receive, send=self.app_send
            ),
        )
        asyncio.create_task(
            self.client.sync_forever(timeout=30000),
        )
        await self.queue.put(
            {
                "type": "matrix.connect",
            }
        )

        LOGGER.info("Started")
        await self.event.wait()
        LOGGER.info("Stopping...")
        await self.client.close()

    async def app_receive(self):
        return await self.queue.get()

    async def app_send(self, message):
        LOGGER.debug(f"app_send {message=}")
        match message["type"]:
            case "matrix.receive":
                LOGGER.error(f"app_send got receive {message=}")
            case "matrix.send":
                await self.matrix_room_send(message["room"], message["body"])
            case "matrix.join":
                print(f"app_send got join {message=}")

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        LOGGER.debug("message_callback {room=} {event=}")
        await self.queue.put(
            {
                "type": "matrix.receive",
                "room": room.display_name,
                "user": room.user_name(event.sender),
                "body": event.body,
            }
        )

    async def join_room(self, room_id: str) -> bool:
        """Try to join the room."""
        LOGGER.debug(f"Join room {room_id=}")

        for _ in range(10):
            try:
                resp = await self.client.join(room_id)
                if not isinstance(resp, JoinError):
                    return True
                match resp.status_code:
                    case "M_UNKNOWN_TOKEN":
                        LOGGER.warning("Reconnecting")
                        await self.client.login(self.args.matrix_pw)
                    case "M_FORBIDDEN" | "M_CONSENT_NOT_GIVEN":
                        LOGGER.error("room access is forbidden")
                        return False
                    case "M_UNKNOWN":
                        LOGGER.error(f"join error: {resp.transport_response.status}")
                        return False
            except LocalProtocolError as e:
                LOGGER.error(f"Send error: {e}")
            LOGGER.warning("Trying again")
        LOGGER.error("Homeserver not responding")
        return False

    async def send_room_message(self, room_id: str, content: Dict[Any, Any]) -> bool:
        """Send a message to a room."""
        LOGGER.debug(f"Sending room message in {room_id=}: {content=}")

        for _ in range(10):
            try:
                resp = await self.client.room_send(
                    room_id=room_id, message_type="m.room.message", content=content
                )
                if not isinstance(resp, RoomSendError):
                    return True
                if resp.status_code == "M_UNKNOWN_TOKEN":
                    LOGGER.warning("Reconnecting")
                    await self.client.login(self.args.matrix_pw)
                else:
                    LOGGER.error(f"room send error {resp=}")
                    return False
            except LocalProtocolError as e:
                LOGGER.error(f"Send error: {e}")
            LOGGER.warning("Trying again")
        LOGGER.error("Homeserver not responding")
        return False

    async def matrix_room_send(self, room, message):
        content = {
            "msgtype": "m.text",
            "body": message,
            "format": "org.matrix.custom.html",
            "formatted_body": markdown(message, extensions=["extra"]),
        }
        await self.send_room_message(room, content)


def get_application(application_name):
    # copy-paste from https://github.com/sivulich/mqttasgi/blob/master/mqttasgi/utils.py
    sys.path.insert(0, ".")
    module_path, object_path = application_name.split(":", 1)
    application = importlib.import_module(module_path)
    for bit in object_path.split("."):
        application = getattr(application, bit)

    return application


if __name__ == "__main__":
    Server().run()
