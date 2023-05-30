from __future__ import annotations

import abc

from django.utils.module_loading import import_string

from . import events

DEFAULT_TOY_SETTINGS_REPOSITORY_PATH = (
    "toy_settings.repositories.filesystem.FileSystemRepo"
)


def get_repository() -> Repository:
    return import_string(DEFAULT_TOY_SETTINGS_REPOSITORY_PATH)()


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
