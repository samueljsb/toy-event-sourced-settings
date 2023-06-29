from __future__ import annotations

import datetime

import pytest

from testing.application.logging import MemoryLogger
from testing.application.unit_of_work import MemoryCommitter
from testing.domain import factories
from testing.domain.queries import MemoryRepo
from toy_settings.application import services
from toy_settings.domain import events


def test_set():
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=[]), committer=committer, logger=logger
    )

    set_at = datetime.datetime.now()
    toy_settings.set("FOO", "42", timestamp=set_at, by="me")

    assert committer.committed == [
        events.Set(key="FOO", value="42", timestamp=set_at, by="me", index=0),
    ]
    assert logger.logged == [("info", "set", (), {"key": "FOO", "value": "42"})]


def test_set_cannot_update_value():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        factories.Set(key="FOO", value="42", timestamp=set_at, by="me"),
    ]
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    with pytest.raises(services.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
    assert logger.logged == [("error", "already set", (), {"key": "FOO"})]


def test_can_change_setting():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        factories.Set(key="FOO", value="42", timestamp=set_at, by="me", index=0),
    ]
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    changed_at = datetime.datetime.now()
    toy_settings.change("FOO", "43", timestamp=changed_at, by="me")

    assert committer.committed == [
        events.Changed(
            key="FOO", new_value="43", timestamp=changed_at, by="me", index=1
        ),
    ]
    assert logger.logged == [("info", "changed", (), {"key": "FOO", "value": "43"})]


def test_cannot_change_non_existent_setting():
    history: list[events.Event] = []
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
    assert logger.logged == [("error", "not set", (), {"key": "FOO"})]


def test_unset_removes_value():
    set_at = datetime.datetime.now()
    history: list[events.Event] = [
        factories.Set(key="FOO", value="42", timestamp=set_at, by="me", index=0),
    ]
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    unset_at = datetime.datetime.now()
    toy_settings.unset("FOO", timestamp=unset_at, by="me")

    assert committer.committed == [
        events.Unset(key="FOO", timestamp=unset_at, by="me", index=1),
    ]
    assert logger.logged == [("info", "unset", (), {"key": "FOO"})]


def test_cannot_change_unset_setting():
    set_at = datetime.datetime.now()
    unset_at = datetime.datetime.now()
    history: list[events.Event] = [
        factories.Set(key="FOO", value="42", timestamp=set_at, by="me"),
        factories.Unset(key="FOO", timestamp=unset_at, by="me"),
    ]
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
    assert logger.logged == [("error", "not set", (), {"key": "FOO"})]


def test_unset_already_unset():
    set_at = datetime.datetime.now()
    unset_at = datetime.datetime.now()
    history: list[events.Event] = [
        factories.Set(key="FOO", value="42", timestamp=set_at, by="me"),
        factories.Unset(key="FOO", timestamp=unset_at, by="me"),
    ]
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=history), committer=committer, logger=logger
    )

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
    assert logger.logged == [("error", "not set", (), {"key": "FOO"})]


def test_unset_never_set():
    committer = MemoryCommitter()
    logger = MemoryLogger()
    toy_settings = services.ToySettings(
        state=MemoryRepo(history=[]), committer=committer, logger=logger
    )

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert committer.committed == []
    assert logger.logged == [("error", "not set", (), {"key": "FOO"})]
