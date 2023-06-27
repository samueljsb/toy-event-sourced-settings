from __future__ import annotations

from testing.domain import factories
from toy_settings.domain import projections


def test_current_settings():
    history = [
        factories.Set(key="set-once", value="42"),
        factories.Set(key="set-and-changed", value="42"),
        factories.Changed(key="set-and-changed", new_value="43"),
        factories.Set(key="set-and-unset", value="42"),
        factories.Unset(key="set-and-unset"),
        factories.Unset(key="never-set"),  # handles unexpected key
    ]

    settings = projections.current_settings(history)

    assert settings == {
        "set-once": "42",
        "set-and-changed": "43",
        # "set-and-unset" is not set
    }
