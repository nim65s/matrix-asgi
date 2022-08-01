#!/usr/bin/env python3
"""Matrix ASGI Server."""
import argparse
import asyncio
import importlib
import logging
import os
import sys
from typing import Dict, Any

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.exceptions import LocalProtocolError
from nio.responses import JoinError, RoomSendError
from nio.rooms import MatrixRoom

LOGGER = logging.getLogger("matrixasgi")


class Server:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=__doc__, prog="python -m matrixasgi"
        )
        parser.add_argument(
            "-u",
            "--matrix-url",
            default=os.environ.get("MATRIX_URL", "https://matrix.org"),
            help="matrix homeserver url. Default: `https://matrix.org`. "
            "Environment variable: `MATRIX_URL`",
        )
        parser.add_argument(
            "-i",
            "--matrix-id",
            help="matrix user-id. Required. Environment variable: `MATRIX_ID`",
            **(
                {"default": os.environ["MATRIX_ID"]}
                if "MATRIX_ID" in os.environ
                else {"required": True}
            ),
        )
        parser.add_argument(
            "-p",
            "--matrix-pw",
            help="matrix password. Required. Environment variable: `MATRIX_PW`",
            **(
                {"default": os.environ["MATRIX_PW"]}
                if "MATRIX_PW" in os.environ
                else {"required": True}
            ),
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="increment verbosity level",
        )

        parser.add_argument(
            "application",
            help="The ASGI application instance to use as path.to.module:application",
        )

        self.args = parser.parse_args()

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
        LOGGER.info("Staring...")
        asyncio.run(self.main())

    async def main(self):
        self.queue = asyncio.Queue()
        await self.client.login(self.args.matrix_pw)
        task_app = asyncio.create_task(
            self.application(
                self.app_scope, receive=self.app_receive, send=self.app_send
            ),
        )
        task_client = asyncio.create_task(
            self.client.sync_forever(timeout=30000),
        )
        await asyncio.gather(task_app, task_client)

    async def app_receive(self):
        return await self.queue.get()

    async def app_send(self, message):
        LOGGER.info(f"app_send {message=}")
        match message["type"]:
            case "matrix.receive":
                print(f"app_send got receive {message=}")
            case "matrix.send":
                print(f"app_send got send {message=}")
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
