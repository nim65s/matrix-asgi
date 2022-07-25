"""Matrix ASGI Server."""
import argparse
import logging

from nio import AsyncClient
from nio.responses import JoinError, RoomSendError

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

        self.args = parser.parse_args()

        self.client = AsyncClient(self.args.matrix_url, self.args.matrix_id)

    async def join_room(room_id: str) -> bool:
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
                        await self.client.login(conf.MATRIX_PW)
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

    async def send_room_message(room_id: str, content Dict[Any, Any]) -> bool:
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
                    await self.client.login(conf.MATRIX_PW)
                else:
                    LOGGER.error(f"room send error {resp=}")
                    return False
            except LocalProtocolError as e:
                LOGGER.error(f"Send error: {e}")
            LOGGER.warning("Trying again")
        LOGGER.error("Homeserver not responding")
        return False
