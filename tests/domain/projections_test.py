from __future__ import annotations

from testing.domain import factories
from toy_settings.domain import projections


def test_current_settings():
    history = [
        factories.Set(key="set-once", value="42", index=0),
        factories.Set(key="set-and-changed", value="42", index=0),
        factories.Changed(key="set-and-changed", new_value="43", index=1),
        factories.Set(key="set-and-unset", value="42", index=0),
        factories.Unset(key="set-and-unset", index=1),
    ]

    settings = projections.current_settings(history)

    assert settings == {
        "set-once": projections.Setting("42", index=0),
        "set-and-changed": projections.Setting("43", index=1),
        "set-and-unset": projections.Setting(None, index=1),
    }
