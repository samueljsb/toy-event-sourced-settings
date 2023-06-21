from __future__ import annotations

from django.db import models


class Event(models.Model):
    event_type = models.CharField(max_length=100)
    event_type_version = models.IntegerField()

    key = models.CharField(max_length=100)

    timestamp = models.DateTimeField()
    payload = models.CharField(max_length=500)
