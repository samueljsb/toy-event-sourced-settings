from __future__ import annotations

import datetime

import pytest

from tests.domain import factories
from toy_settings.domain import services
from toy_settings.repositories.memory import MemoryRepo


def test_set():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "42"}


def test_set_cannot_update_value():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    with pytest.raises(services.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "42"}


def test_can_change_setting():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.change("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "43"}


def test_cannot_change_non_existent_setting():
    repo = MemoryRepo([])
    toy_settings = services.ToySettings(repo=repo)

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")


def test_cannot_change_unset_setting():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
            factories.Unset(key="FOO"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")


def test_unset_removes_value():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    unset_at = datetime.datetime.now()
    new_events = toy_settings.unset("FOO", timestamp=unset_at, by="me")

    assert new_events == (factories.Unset(key="FOO", timestamp=unset_at, by="me"),)


def test_unset_already_unset():
    repo = MemoryRepo(
        [
            factories.Set(key="FOO", value="42"),
            factories.Unset(key="FOO"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")


def test_unset_never_set():
    repo = MemoryRepo([])
    toy_settings = services.ToySettings(repo=repo)

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")
