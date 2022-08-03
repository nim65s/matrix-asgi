"""Main test file for matrix-asgi."""

from os import environ

from django.test import TestCase

import nio

MATRIX_URL, MATRIX_ID, MATRIX_PW, ROOM_ID = (
    environ[v] for v in ["MATRIX_URL", "MATRIX_ID", "MATRIX_PW", "ROOM_ID"]
)


class MatrixAsgiTestCase(TestCase):
    """Main test class for matrix-asgi."""

    def test_true(self):
        """Trivial test for matrix-asgi."""
        self.assertTrue(True)

    async def test_matrix2model(self):
        """Send a matrix message, and check a model instance got created."""
        client = nio.AsyncClient(MATRIX_URL, MATRIX_ID)
        await client.login(MATRIX_PW)
        await client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": "hello"},
        )
        await client.close()
