"""Consumers for django_app to test matrix-asgi."""
import os

from matrix_asgi.consumers import MatrixConsumer


class ChatMatrixConsumer(MatrixConsumer):
    """A MatrixConsumer which interract with a Django model."""

    startswith = "!"

    async def connect(self):
        """Register model2matrix group."""
        await self.channel_layer.group_add("model2matrix", self.channel_name)

    async def disconnect(self, close_code):
        """Unregister model2matrix group."""
        await self.channel_layer.group_discard("model2matrix", self.channel_name)

    async def receive(self, matrix_message):
        """Receive a Matrix Message and save it into a Django Model."""
        await self.channel_layer.group_send(
            "matrix2model",
            {
                "type": "matrix.message",
                "message": matrix_message,
            },
        )

    async def chat_message(self, message):
        """Joker."""
        await self.matrix_send(os.environ["ROOM_ID"], message["message"])
