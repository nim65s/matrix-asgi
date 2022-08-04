"""Models for django_app."""
from django.db import models


class Message(models.Model):
    """Send and Receive Matrix messages."""

    user = models.CharField(max_length=250)
    room = models.CharField(max_length=250)
    type = models.CharField(max_length=250)
    body = models.TextField()
