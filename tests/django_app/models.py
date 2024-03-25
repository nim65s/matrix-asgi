"""Models for django_app."""

from django.db import models

from channels.layers import get_channel_layer


class Message(models.Model):
    """Send and Receive Matrix messages."""

    user = models.CharField(max_length=250)
    room = models.CharField(max_length=250)
    type = models.CharField(max_length=250)
    body = models.TextField()

    async def to_matrix(self):
        """Forward this Message to Matrix."""
        layer = get_channel_layer()
        await layer.group_send(
            "model2matrix",
            {
                "type": "django_app.message",
                "room": self.room,
                "body": self.body,
            },
        )
