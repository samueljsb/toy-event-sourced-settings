from __future__ import annotations

import datetime

import pytest

from toy_settings.application import services
from toy_settings.repositories.memory import MemoryRepo
from toy_settings.units_of_work.memory import MemoryUoW


def test_set():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert state.all_settings() == {"FOO": "42"}
    assert uow.committed is True


def test_set_cannot_update_value():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    with pytest.raises(services.AlreadySet):
        toy_settings.set("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert state.all_settings() == {"FOO": "42"}
    assert uow.committed is False


def test_can_change_setting():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.change("FOO", "43", timestamp=datetime.datetime.now(), by="me")

    assert state.all_settings() == {"FOO": "43"}
    assert uow.committed is True


def test_cannot_change_non_existent_setting():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    # check we are not allowed to change a setting that does not exist
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert uow.committed is False


def test_unset_removes_value():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert state.all_settings() == {}
    assert uow.committed is True


def test_cannot_change_unset_setting():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    # check we are not allowed to change a setting that has been unset
    with pytest.raises(services.NotSet):
        toy_settings.change("FOO", "42", timestamp=datetime.datetime.now(), by="me")

    assert uow.committed is False


def test_unset_already_unset():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert uow.committed is False


def test_unset_never_set():
    uow = MemoryUoW.new()
    state = MemoryRepo()
    toy_settings = services.ToySettings(state=state, uow=uow, max_wait_seconds=0)

    # check we are not allowed to unset it again
    with pytest.raises(services.NotSet):
        toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert uow.committed is False
