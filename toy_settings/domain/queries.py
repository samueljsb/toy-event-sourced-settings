from __future__ import annotations

import abc

from . import events
from . import projections


class StaleState(Exception):
    """
    An event could not be recorded because the state has changed.
    """


class Repository(abc.ABC):
    @abc.abstractmethod
    def events_for_key(self, key: str) -> list[events.Event]:
        """Retrieve the events for this key in chronological order."""
        ...

    @abc.abstractmethod
    def get_setting(self, key: str) -> projections.Setting:
        """Get the current state of a setting."""
        ...

    @abc.abstractmethod
    def current_value(self, key: str) -> str | None:
        """Get the current value of a setting."""
        ...

    @abc.abstractmethod
    def all_settings(self) -> dict[str, str]:
        """Get the current value of all settings."""
        ...
