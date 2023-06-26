from __future__ import annotations

import datetime

import pytest

from testing.application.unit_of_work import MemoryCommitter
from testing.domain.queries import MemoryRepo
from toy_settings.application import services
from toy_settings.domain import events


def test_set():
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=[]), committer=committer, max_wait_seconds=0
    )

    set_at = datetime.datetime.now()
    toy_settings.set("FOO", "42", timestamp=set_at, by="me")

    assert committer.committed == [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
    ]


def test_set_cannot_update_value():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
    ]
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    with pytest.raises(services.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []


def test_can_change_setting():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
    ]
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    changed_at = datetime.datetime.now()
    toy_settings.change("FOO", "43", timestamp=changed_at, by="me")

    assert committer.committed == [
        events.Changed(key="FOO", new_value="43", timestamp=changed_at, by="me"),
    ]


def test_cannot_change_non_existent_setting():
    history: list[events.Event] = []
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []


def test_unset_removes_value():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
    ]
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    unset_at = datetime.datetime.now()
    toy_settings.unset("FOO", timestamp=unset_at, by="me")

    assert committer.committed == [
        events.Unset(key="FOO", timestamp=unset_at, by="me"),
    ]


def test_cannot_change_unset_setting():
    set_at = datetime.datetime.now()
    unset_at = datetime.datetime.now()
    history: list[events.Event] = [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
        events.Unset(key="FOO", timestamp=unset_at, by="me"),
    ]
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []


def test_unset_already_unset():
    set_at = datetime.datetime.now()
    unset_at = datetime.datetime.now()
    history: list[events.Event] = [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me"),
        events.Unset(key="FOO", timestamp=unset_at, by="me"),
    ]
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, max_wait_seconds=0
    )

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []


def test_unset_never_set():
    committer = MemoryCommitter()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=[]), committer=committer, max_wait_seconds=0
    )

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
