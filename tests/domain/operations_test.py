from __future__ import annotations

import datetime

import pytest

from testing.domain import factories
from testing.domain.queries import MemoryRepo
from toy_settings.domain import events
from toy_settings.domain import operations


def test_set():
    repo = MemoryRepo()
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    set_at = datetime.datetime.now()
    toy_settings.set("FOO", "42", timestamp=set_at, by="me")

    assert new_events == [
        factories.Set(
            key="FOO",
            value="42",
            timestamp=set_at,
            by="me",
            index=0,
        )
    ]


def test_set_cannot_update_value():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
        ]
    )
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    with pytest.raises(operations.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert new_events == []


def test_can_change_setting():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42", index=0),
        ]
    )
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    changed_at = datetime.datetime.now()
    toy_settings.change("FOO", "43", timestamp=changed_at, by="me")

    assert new_events == [
        factories.Changed(
            key="FOO",
            new_value="43",
            timestamp=changed_at,
            by="me",
            index=1,
        )
    ]


def test_cannot_change_non_existent_setting():
    repo = MemoryRepo([])
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(operations.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert new_events == []


def test_cannot_change_unset_setting():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
            factories.Unset(key="FOO"),
        ]
    )
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(operations.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert new_events == []


def test_unset_removes_value():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42", index=0),
        ]
    )
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    unset_at = datetime.datetime.now()
    toy_settings.unset("FOO", timestamp=unset_at, by="me")

    assert new_events == [
        factories.Unset(
            key="FOO",
            timestamp=unset_at,
            by="me",
            index=1,
        )
    ]


def test_unset_already_unset():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
            factories.Unset(key="FOO"),
        ]
    )
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    # check we are not allowed to unset it again
    with pytest.raises(operations.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert new_events == []


def test_unset_never_set():
    repo = MemoryRepo([])
    new_events: list[events.Event] = []
    toy_settings = operations.ToySettings(state=repo, new_events=new_events)

    # check we are not allowed to unset it again
    with pytest.raises(operations.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert new_events == []
