from __future__ import annotations

from typing import Iterable

from . import events


def normalize_key(key: str) -> str:
    return key.strip().replace(" ", "_").replace("-", "_").upper()


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
