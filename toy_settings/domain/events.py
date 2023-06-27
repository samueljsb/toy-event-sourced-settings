from __future__ import annotations

import abc
import datetime

import attrs


@attrs.frozen
class Event(abc.ABC):
    index: int
    timestamp: datetime.datetime

    key: str


@attrs.frozen
class Set(Event):
    value: str

    by: str


@attrs.frozen
class Changed(Event):
    new_value: str

    by: str


@attrs.frozen
class Unset(Event):
    by: str
