from channels.consumer import AsyncConsumer

import logging

logger = logging.getLogger(__name__)


class MatrixConsumer(AsyncConsumer):
    startswith = ""

    async def connect(self):
        pass

    async def receive(self, matrix_message):
        pass

    async def matrix_connect(self, event):
        await self.connect()

    async def matrix_receive(self, event):
        if self.startswith:
            if event["body"].startswith(self.startswith):
                event["body"] = event["body"].removeprefix(self.startswith)
            else:
                return
        await self.receive(event)

    async def matrix_send(self, room, body):
        await self.send({"type": "matrix.send", "room": room, "body": body})
