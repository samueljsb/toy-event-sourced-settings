from __future__ import annotations

import cattrs.preconf.json
from django.db import models

from toy_settings.domain import events

EVENT_TYPES: dict[type[events.Event], tuple[str, int]] = {
    events.Set: ("Set", 1),
    events.Changed: ("Changed", 1),
    events.Unset: ("Unset", 1),
}


def event_type(event_type: str, version: int) -> type[events.Event]:
    return {v: k for k, v in EVENT_TYPES.items()}[(event_type, version)]


class Event(models.Model):
    event_type = models.CharField(max_length=100)
    event_type_version = models.IntegerField()

    key = models.CharField(max_length=100)

    timestamp = models.DateTimeField()
    payload = models.CharField(max_length=500)
    payload_converter = cattrs.preconf.json.make_converter()
