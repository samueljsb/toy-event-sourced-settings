from __future__ import annotations

from toy_settings.domain import events
from toy_settings.domain import projections
from toy_settings.domain import storage


class MemoryRepo(storage.Repository):
    def __init__(self, history: list[events.Event] | None = None) -> None:
        self.events: list[events.Event] = history or []

    def record(self, event: events.Event) -> None:
        self.events.append(event)

    def events_for_key(self, key: str) -> list[events.Event]:
        return sorted(
            (event for event in self.events if event.key == key),
            key=lambda e: e.timestamp,
        )

    # projections

    def current_value(self, key: str) -> str | None:
        return self.all_settings().get(key, None)

    def all_settings(self) -> dict[str, str]:
        return projections.current_settings(
            sorted(
                self.events,
                key=lambda e: e.timestamp,
            )
        )


MEMORY_REPO = MemoryRepo()
