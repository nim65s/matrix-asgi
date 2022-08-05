"""Matrix ASGI Consumers."""
from channels.consumer import AsyncConsumer

import logging

logger = logging.getLogger(__name__)


class MatrixConsumer(AsyncConsumer):
    """MatrixConsumer to be subclassed by users."""

    startswith = ""

    async def connect(self):
        """Connect method to be subclassed by users."""
        pass  # pragma: no cover

    async def disconnect(self):
        """Disonnect method to be subclassed by users."""
        pass  # pragma: no cover

    async def receive(self, matrix_message):
        """Receive method to be subclassed by users."""
        pass  # pragma: no cover

    async def matrix_connect(self, event):
        """Initialize connection."""
        await self.connect()

    async def matrix_disconnect(self, event):
        """Initialize connection."""
        await self.disconnect(0)

    async def matrix_receive(self, event):
        """Handle an incoming message from Matrix: forward it to Channels.

        If `startswith` is defined, this will filter out
        messages not starting with `startswith`.
        """
        if self.startswith:
            if event["body"].startswith(self.startswith):
                event["body"] = event["body"].removeprefix(self.startswith)
            else:
                return
        await self.receive(event)

    async def matrix_send(self, room, body):
        """Handle an incoming message from Channels: forward it to Matrix."""
        await self.send({"type": "matrix.send", "room": room, "body": body})
