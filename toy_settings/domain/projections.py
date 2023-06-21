from __future__ import annotations

from functools import singledispatch
from typing import Iterable

from . import events


def current_settings(history: Iterable[events.Event]) -> dict[str, str]:
    settings: dict[str, str] = {}
    for event in sorted(history, key=lambda e: e.timestamp):
        _handle_event(event, settings)

    return settings


@singledispatch
def _handle_event(event: events.Event, settings: dict[str, str]) -> None:
    raise TypeError(f"unrecognised event type: {type(event)!r}")  # pragma: no cover


@_handle_event.register
def _(event: events.Set, settings: dict[str, str]) -> None:
    settings[event.key] = event.value


@_handle_event.register
def _(event: events.Changed, settings: dict[str, str]) -> None:
    settings[event.key] = event.new_value


@_handle_event.register
def _(event: events.Unset, settings: dict[str, str]) -> None:
    try:
        del settings[event.key]
    except KeyError:
        pass
