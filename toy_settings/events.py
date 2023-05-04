from __future__ import annotations

import abc
import datetime

import attrs


@attrs.frozen
class Event(abc.ABC):
    id: str
    timestamp: datetime.datetime
    by: str

    key: str


@attrs.frozen
class Set(Event):
    value: str


@attrs.frozen
class Unset(Event):
    pass
