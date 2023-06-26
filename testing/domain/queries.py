from __future__ import annotations

import attrs

from toy_settings.domain import events
from toy_settings.domain import projections
from toy_settings.domain import queries


@attrs.frozen
class MemoryRepo(queries.Repository):
    history: list[events.Event] = attrs.field(factory=list)

    def events_for_key(self, key: str) -> list[events.Event]:  # pragma: no cover
        return sorted(
            (event for event in self.history if event.key == key),
            key=lambda e: e.timestamp,
        )

    def current_value(self, key: str) -> str | None:
        return self.all_settings().get(key, None)

    def all_settings(self) -> dict[str, str]:
        return projections.current_settings(
            sorted(
                self.history,
                key=lambda e: e.timestamp,
            )
        )
