from __future__ import annotations

import abc
import datetime
import json
import os.path
from pathlib import Path
from typing import Any
from typing import Generic
from typing import TypeVar

from toy_settings import events
from toy_settings import projections
from toy_settings import storage

_TEvent = TypeVar("_TEvent", bound=events.Event)


class Codec(abc.ABC, Generic[_TEvent]):
    @abc.abstractmethod
    def encode(self, event: _TEvent) -> dict[str, str]:
        ...

    @abc.abstractmethod
    def decode(self, payload: dict[str, str]) -> _TEvent:
        ...


class SetCodec(Codec[events.Set]):
    def encode(self, event: events.Set) -> dict[str, str]:
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "by": event.by,
            "key": event.key,
            "value": event.value,
        }

    def decode(self, payload: dict[str, str]) -> events.Set:
        return events.Set(
            id=payload["id"],
            timestamp=datetime.datetime.fromisoformat(payload["timestamp"]),
            by=payload["by"],
            key=payload["key"],
            value=payload["value"],
        )


class UnsetCodec(Codec[events.Unset]):
    def encode(self, event: events.Unset) -> dict[str, str]:
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "by": event.by,
            "key": event.key,
        }

    def decode(self, payload: dict[str, str]) -> events.Unset:
        return events.Unset(
            id=payload["id"],
            timestamp=datetime.datetime.fromisoformat(payload["timestamp"]),
            by=payload["by"],
            key=payload["key"],
        )


CODECS: tuple[tuple[str, type[events.Event], Codec[Any]], ...] = (
    ("set", events.Set, SetCodec()),
    ("unset", events.Unset, UnsetCodec()),
)


def encode(event: events.Event) -> str:
    try:
        event_type, codec = {item[1]: (item[0], item[2]) for item in CODECS}[
            type(event)
        ]
    except KeyError as exc:
        raise TypeError(f"unrecognised event type: {type(event)!r}") from exc

    data = {
        "event_type": event_type,
        "payload": codec.encode(event),
    }
    return json.dumps(data)


def decode(raw_data: str) -> events.Event:
    data: dict[str, Any] = json.loads(raw_data)

    event_type = data["event_type"]
    try:
        codec = {item[0]: item[2] for item in CODECS}[event_type]
    except KeyError as exc:
        raise ValueError(f"unrecognised event type: {event_type!r}") from exc

    return codec.decode(data["payload"])


def _xdg_state_home() -> Path:
    xdg_state_home = os.getenv("XDG_STATE_HOME")
    if xdg_state_home and os.path.isabs(xdg_state_home):
        return Path(xdg_state_home)
    else:
        return Path("~/.local/state").expanduser()


class FileSystemRepo(storage.Repository):
    def __init__(self) -> None:
        self.root = _xdg_state_home() / "toy-settings"
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, key: str) -> Path:
        dir = self.root / key
        dir.mkdir(exist_ok=True)
        return dir

    def record(self, event: events.Event) -> None:
        file = self._dir(event.key) / event.id
        file.touch()
        file.write_text(encode(event))

    def events_for_key(self, key: str) -> list[events.Event]:
        return sorted(
            (decode(file.read_text()) for file in self._dir(key).glob("*")),
            key=lambda e: e.timestamp,
        )

    # projections

    def current_value(self, key: str) -> str | None:
        return projections.current_value(key, self.events_for_key(key))

    def all_settings(self) -> dict[str, str]:
        all_events = sorted(
            (
                decode(file.read_text())
                for file in self.root.rglob("*")
                if file.is_file()
            ),
            key=lambda e: e.timestamp,
        )
        return projections.current_settings(all_events)
