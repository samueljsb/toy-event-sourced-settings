from __future__ import annotations

from collections import defaultdict
from functools import singledispatch
from typing import Iterable

import attrs

from . import events


@attrs.define
class Setting:
    value: str | None = None
    index: int = -1


def current_settings(history: Iterable[events.Event]) -> defaultdict[str, Setting]:
    settings: defaultdict[str, Setting] = defaultdict(lambda: Setting())
    for event in sorted(history, key=lambda e: e.timestamp):
        _handle_event(event, settings)

    return settings


@singledispatch
def _handle_event(event: events.Event, settings: dict[str, Setting]) -> None:
    raise TypeError(f"unrecognised event type: {type(event)!r}")  # pragma: no cover


@_handle_event.register
def _(event: events.Set, settings: dict[str, Setting]) -> None:
    settings[event.key].value = event.value
    settings[event.key].index = event.index


@_handle_event.register
def _(event: events.Changed, settings: dict[str, Setting]) -> None:
    settings[event.key].value = event.new_value
    settings[event.key].index = event.index


@_handle_event.register
def _(event: events.Unset, settings: dict[str, Setting]) -> None:
    settings[event.key].value = None
    settings[event.key].index = event.index
