from __future__ import annotations

import datetime

import pytest

from toy_settings import events
from toy_settings import projections


def _set_event(key: str, value: str, id: str) -> events.Set:
    return events.Set(
        id=id, timestamp=datetime.datetime.now(), by="me", key=key, value=value
    )


def _changed_event(key: str, new_value: str, id: str) -> events.Changed:
    return events.Changed(
        id=id, timestamp=datetime.datetime.now(), by="me", key=key, new_value=new_value
    )


def _unset_event(key: str, id: str) -> events.Unset:
    return events.Unset(id=id, timestamp=datetime.datetime.now(), by="me", key=key)


def test_current_settings():
    history = [
        _set_event("set-once", "42", id="1"),
        _set_event("set-and-changed", "42", id="2"),
        _changed_event("set-and-changed", "43", id="3"),
        _set_event("set-and-unset", "42", id="4"),
        _unset_event("set-and-unset", id="5"),
        _unset_event("never-set", id="6"),  # handles unexpected key
    ]

    settings = projections.current_settings(history)

    assert settings == {
        "set-once": "42",
        "set-and-changed": "43",
        # "set-and-unset" is not set
    }


@pytest.mark.parametrize(
    ("key", "expected_value"),
    (
        ("set-once", "42"),
        ("set-and-changed", "43"),
        ("set-and-unset", None),
        ("never-set", None),
        ("never-mentioned", None),
    ),
)
def test_current_value(key, expected_value):
    history = [
        _set_event("set-once", "42", id="1"),
        _set_event("set-and-changed", "42", id="2"),
        _changed_event("set-and-changed", "43", id="3"),
        _set_event("set-and-unset", "42", id="4"),
        _unset_event("set-and-unset", id="5"),
        _unset_event("never-set", id="6"),
    ]

    value = projections.current_value(key, history)

    assert value == expected_value
