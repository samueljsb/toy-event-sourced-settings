from __future__ import annotations

import abc

from . import events


def get_repository() -> Repository:
    from toy_settings.repositories import filesystem

    return filesystem.FileSystemRepo()


class Repository(abc.ABC):
    @abc.abstractmethod
    def record(self, event: events.Event) -> None:
        """Record a new event."""
        ...

    @abc.abstractmethod
    def events_for_key(self, key: str) -> list[events.Event]:
        """Retrieve the events for this key in chronological order."""
        ...

    # projections

    @abc.abstractmethod
    def current_value(self, key: str) -> str | None:
        """Get the current value of a setting."""
        ...

    @abc.abstractmethod
    def all_settings(self) -> dict[str, str]:
        """Get the current value of all settings."""
        ...
