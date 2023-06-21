from __future__ import annotations

import datetime

from toy_settings.domain import events
from toy_settings.domain import projections


def _set_event(key: str, value: str) -> events.Set:
    return events.Set(timestamp=datetime.datetime.now(), by="me", key=key, value=value)


def _changed_event(key: str, new_value: str) -> events.Changed:
    return events.Changed(
        timestamp=datetime.datetime.now(), by="me", key=key, new_value=new_value
    )


def _unset_event(key: str) -> events.Unset:
    return events.Unset(timestamp=datetime.datetime.now(), by="me", key=key)


def test_current_settings():
    history = [
        _set_event("set-once", "42"),
        _set_event("set-and-changed", "42"),
        _changed_event("set-and-changed", "43"),
        _set_event("set-and-unset", "42"),
        _unset_event("set-and-unset"),
        _unset_event("never-set"),  # handles unexpected key
    ]

    settings = projections.current_settings(history)

    assert settings == {
        "set-once": "42",
        "set-and-changed": "43",
        # "set-and-unset" is not set
    }
