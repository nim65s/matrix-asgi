"""Main test file for matrix-asgi."""

import asyncio
import os

from asgiref.sync import sync_to_async
from django.test import TestCase
import nio

from matrix_asgi.server import AsgiMatrixServer

from .models import Message

MATRIX_URL, MATRIX_ID, MATRIX_PW, ROOM_ID = (
    os.environ[v] for v in ["MATRIX_URL", "MATRIX_ID", "MATRIX_PW", "ROOM_ID"]
)


class MatrixAsgiTestingInstance:
    """Async context to run an AsgiMatrixServer."""

    def __init__(self):
        """Declare members."""
        self.event = None

    async def __aenter__(self):
        """Start the server."""
        server = AsgiMatrixServer(
            application="django_project.asgi:application",
            verbosity=3,
        )
        self.event = asyncio.Event()
        await server.main(self.event)
        asyncio.create_task(server.serve())

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Close the server."""
        self.event.set()


class MatrixAsgiTestCase(TestCase):
    """Main test class for matrix-asgi."""

    def test_true(self):
        """Trivial test for matrix-asgi."""
        self.assertTrue(True)

    async def test_matrix2model(self):
        """Send a matrix message, and check a model instance got created."""
        async with MatrixAsgiTestingInstance():
            self.assertEqual(await sync_to_async(Message.objects.count)(), 0)

            client = nio.AsyncClient(MATRIX_URL, MATRIX_ID)
            await client.login(MATRIX_PW)
            ret = await client.room_send(
                room_id=ROOM_ID,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": "!hello"},
            )
            self.assertEqual(ret.transport_response.status, 200)
            await client.close()
            await asyncio.sleep(2)
            self.assertEqual(await sync_to_async(Message.objects.count)(), 1)
            message = await sync_to_async(Message.objects.get)()
            self.assertEqual(message.body, "hello")
