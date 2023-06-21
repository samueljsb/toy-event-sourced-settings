from __future__ import annotations

from typing import Iterable

from . import events


def current_settings(history: Iterable[events.Event]) -> dict[str, str]:
    settings = {}
    for event in sorted(history, key=lambda e: e.timestamp):
        if isinstance(event, events.Set):
            settings[event.key] = event.value
        elif isinstance(event, events.Changed):
            settings[event.key] = event.new_value
        elif isinstance(event, events.Unset):
            try:
                del settings[event.key]
            except KeyError:
                pass
        else:  # pragma: no cover
            raise TypeError(f"unrecognised event type: {type(event)!r}")

    return settings
