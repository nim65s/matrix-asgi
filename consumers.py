from channels.consumer import AsyncConsumer

import logging

logger = logging.getLogger(__name__)


class MatrixConsumer(AsyncConsumer):
    async def connect(self):
        pass

    async def receive(self, matrix_message):
        pass

    async def send(self, matrix_message):
        pass

    async def matrix_receive(self, matrix_message):
        await self.receive(matrix_message)
