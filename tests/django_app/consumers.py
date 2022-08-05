"""Consumers for django_app to test matrix-asgi."""
from matrix_asgi.consumers import MatrixConsumer

from .models import Message


class DjangoAppMatrixConsumer(MatrixConsumer):
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
        await Message.objects.acreate(**matrix_message)

    async def django_app_message(self, message):
        """Send a Matrix Message from django model."""
        await self.matrix_send(message["room"], message["body"])
