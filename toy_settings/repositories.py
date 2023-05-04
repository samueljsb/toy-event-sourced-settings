from __future__ import annotations

import abc

from . import events


class Repository(abc.ABC):
    @abc.abstractmethod
    def record(self, event: events.Event) -> None:
        ...

    @abc.abstractmethod
    def current_value(self, key: str) -> str | None:
        ...

    @abc.abstractmethod
    def all_settings(self) -> dict[str, str]:
        ...

    @abc.abstractmethod
    def events_for_key(self, key: str) -> list[events.Event]:
        ...


class MemoryRepo(Repository):
    def __init__(self) -> None:
        self.events: list[events.Event] = []

    def record(self, event: events.Event) -> None:
        self.events.append(event)

    def current_value(self, key: str) -> str | None:
        events_ = sorted(self.events_for_key(key), key=lambda e: e.timestamp)

        try:
            last_event = events_.pop()
        except IndexError:
            return None

        if isinstance(last_event, events.Set):
            return last_event.value
        else:
            return None

    def all_settings(self) -> dict[str, str]:
        settings = {}
        for event in self.events:
            if isinstance(event, events.Set):
                settings[event.key] = event.value
            elif isinstance(event, events.Unset):
                try:
                    del settings[event.key]
                except KeyError:
                    pass
            else:
                raise TypeError(f"unrecognised event type: {type(event)!r}")

        return settings

    def events_for_key(self, key: str) -> list[events.Event]:
        return [event for event in self.events if event.key == key]


MEMORY_REPO = MemoryRepo()
