from __future__ import annotations

import datetime

import pytest

from toy_settings.services import services


def test_set():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "42"}


def test_set_cannot_update_value():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    with pytest.raises(services.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "42"}


def test_can_change_setting():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.change("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "43"}


def test_cannot_change_non_existent_setting():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")


def test_unset_removes_value():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {}


def test_cannot_change_unset_setting():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")


def test_unset_already_unset():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")


def test_unset_never_set():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo, max_wait_seconds=0)

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")
