from __future__ import annotations

import abc
import datetime
import json
import os
from pathlib import Path
from typing import Any
from typing import Generic
from typing import TypeVar

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


# In-memory


class MemoryRepo(Repository):
    def __init__(self, history: list[events.Event] | None = None) -> None:
        self.events: list[events.Event] = history or []

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

# File system


_TEvent = TypeVar("_TEvent", bound=events.Event)


class Serializer(abc.ABC, Generic[_TEvent]):
    @abc.abstractmethod
    def build_payload(self, event: _TEvent) -> dict[str, str]:
        ...

    @abc.abstractmethod
    def unpack(self, payload: dict[str, str]) -> _TEvent:
        ...


class SetSerializer(Serializer[events.Set]):
    def build_payload(self, event: events.Set) -> dict[str, str]:
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "by": event.by,
            "key": event.key,
            "value": event.value,
        }

    def unpack(self, payload: dict[str, str]) -> events.Set:
        return events.Set(
            id=payload["id"],
            timestamp=datetime.datetime.fromisoformat(payload["timestamp"]),
            by=payload["by"],
            key=payload["key"],
            value=payload["value"],
        )


class UnsetSerializer(Serializer[events.Unset]):
    def build_payload(self, event: events.Unset) -> dict[str, str]:
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "by": event.by,
            "key": event.key,
        }

    def unpack(self, payload: dict[str, str]) -> events.Unset:
        return events.Unset(
            id=payload["id"],
            timestamp=datetime.datetime.fromisoformat(payload["timestamp"]),
            by=payload["by"],
            key=payload["key"],
        )


SERIALIZERS: tuple[tuple[str, type[events.Event], Serializer[Any]], ...] = (
    ("set", events.Set, SetSerializer()),
    ("unset", events.Unset, UnsetSerializer()),
)


def serialize(event: events.Event) -> str:
    try:
        event_type, serializer = {item[1]: (item[0], item[2]) for item in SERIALIZERS}[
            type(event)
        ]
    except KeyError as exc:
        raise TypeError(f"unrecognised event type: {type(event)!r}") from exc

    data = {
        "event_type": event_type,
        "payload": serializer.build_payload(event),
    }
    return json.dumps(data)


def deserialize(raw_data: str) -> events.Event:
    data: dict[str, Any] = json.loads(raw_data)

    event_type = data["event_type"]
    try:
        serializer = {item[0]: item[2] for item in SERIALIZERS}[event_type]
    except KeyError as exc:
        raise ValueError(f"unrecognised event type: {event_type!r}") from exc

    return serializer.unpack(data["payload"])


class FileSystemRepo(Repository):
    def __init__(self) -> None:
        XDG_STATE_HOME = os.getenv("XDG_STATE_HOME")
        if XDG_STATE_HOME and os.path.isabs(XDG_STATE_HOME):
            xdg_state_home = Path(XDG_STATE_HOME)
        else:
            xdg_state_home = Path("~/.local/state").expanduser()

        self.root = xdg_state_home / "toy-settings"
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, key: str) -> Path:
        dir = self.root / key
        dir.mkdir(exist_ok=True)
        return dir

    def record(self, event: events.Event) -> None:
        file = self._dir(event.key) / event.id
        file.touch()
        file.write_text(serialize(event))

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
        all_events = sorted(
            (
                deserialize(file.read_text())
                for file in self.root.rglob("*")
                if file.is_file()
            ),
            key=lambda e: e.timestamp,
        )

        settings = {}
        for event in all_events:
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
        return [deserialize(file.read_text()) for file in self._dir(key).glob("*")]
