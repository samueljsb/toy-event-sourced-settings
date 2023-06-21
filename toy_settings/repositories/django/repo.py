from __future__ import annotations

import json

import cattrs.preconf.json
from django.db.models import Q

from toy_settings.domain import events
from toy_settings.domain import projections
from toy_settings.domain import storage

from . import models

EVENT_TYPES: dict[type[events.Event], tuple[str, int]] = {
    events.Set: ("Set", 1),
    events.Changed: ("Changed", 1),
    events.Unset: ("Unset", 1),
}


def _event_type(event_type: str, version: int) -> type[events.Event]:
    return {v: k for k, v in EVENT_TYPES.items()}[(event_type, version)]


converter = cattrs.preconf.json.make_converter()


def _to_json(event: events.Event) -> str:
    payload = converter.unstructure(event)
    return json.dumps(payload)


def _from_json(payload: str, event_type: str, version: int) -> events.Event:
    parsed = json.loads(payload)
    return converter.structure(parsed, _event_type(event_type, version))


class DjangoRepo(storage.Repository):
    def record(self, event: events.Event) -> None:
        """Record a new event.

        Raises:
            StaleState: The state has changed and recording is no longer safe.
        """
        event_type, event_type_version = EVENT_TYPES[type(event)]
        models.Event.objects.create(
            event_type=event_type,
            event_type_version=event_type_version,
            timestamp=event.timestamp,
            key=event.key,
            payload=_to_json(event),
        )

    # projections

    def _events(self, filter: Q = Q()) -> list[events.Event]:
        return [
            _from_json(evt.payload, evt.event_type, evt.event_type_version)
            for evt in models.Event.objects.filter(filter).order_by("timestamp")
        ]

    def events_for_key(self, key: str) -> list[events.Event]:
        """Retrieve the events for this key in chronological order."""
        return self._events(Q(key=key))

    def current_value(self, key: str) -> str | None:
        """Get the current value of a setting."""
        return projections.current_settings(self.events_for_key(key)).get(key)

    def all_settings(self) -> dict[str, str]:
        """Get the current value of all settings."""
        return projections.current_settings(self._events())
