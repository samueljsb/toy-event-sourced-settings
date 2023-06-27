from __future__ import annotations

from django.db.models import Q

from toy_settings.domain import events
from toy_settings.domain import projections
from toy_settings.domain import queries

from . import models


class DjangoRepo(queries.Repository):
    def _events(self, filter: Q = Q()) -> list[events.Event]:
        return [
            models.Event.payload_converter.loads(
                evt.payload, models.event_type(evt.event_type, evt.event_type_version)
            )
            for evt in models.Event.objects.filter(filter).order_by("timestamp")
        ]

    def events_for_key(self, key: str) -> list[events.Event]:
        """Retrieve the events for this key in chronological order."""
        return self._events(Q(key=key))

    def get_setting(self, key: str) -> projections.Setting:
        return projections.current_settings(self.events_for_key(key))[key]

    def current_value(self, key: str) -> str | None:
        """Get the current value of a setting."""
        return self.get_setting(key).value

    def all_settings(self) -> dict[str, str]:
        """Get the current value of all settings."""
        return {
            key: setting.value
            for key, setting in projections.current_settings(self._events()).items()
            if setting.value is not None
        }
