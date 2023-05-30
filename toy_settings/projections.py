from __future__ import annotations

from typing import Iterable

from . import events


def current_settings(history: Iterable[events.Event]) -> dict[str, str]:
    settings = {}
    for event in sorted(history, key=lambda e: e.timestamp):
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


def current_value(key: str, history: Iterable[events.Event]) -> str | None:
    ordered_history = sorted(
        (event for event in history if event.key == key),
        key=lambda e: e.timestamp,
    )
    try:
        last_event = ordered_history.pop()
    except IndexError:
        return None

    if isinstance(last_event, events.Set):
        return last_event.value
    else:
        return None
