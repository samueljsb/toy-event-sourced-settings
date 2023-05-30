import datetime

from toy_settings import events
from toy_settings import services
from toy_settings.repositories.memory import MemoryRepo


def _set_event(key: str, value: str, id: str) -> events.Set:
    return events.Set(
        id=id, timestamp=datetime.datetime.now(), by="me", key=key, value=value
    )


def _unset_event(key: str, id: str) -> events.Unset:
    return events.Unset(id=id, timestamp=datetime.datetime.now(), by="me", key=key)


def test_set_normalizes_key():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.set("foo", "42", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "42"}


def test_set_updates_value():
    repo = MemoryRepo()
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.set("FOO", "42", timestamp=datetime.datetime.now(), by="me")
    toy_settings.set("foo", "43", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {"FOO": "43"}


def test_unset_removes_value():
    repo = MemoryRepo(
        [
            _set_event("FOO", "42", id="1"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {}


def test_unset_already_unset():
    repo = MemoryRepo(
        [
            _set_event("FOO", "42", id="1"),
            _unset_event("FOO", id="2"),
        ]
    )
    toy_settings = services.ToySettings(repo=repo)

    # check doing it twice has no effect
    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {}


def test_unset_never_set():
    repo = MemoryRepo([])
    toy_settings = services.ToySettings(repo=repo)

    toy_settings.unset("FOO", timestamp=datetime.datetime.now(), by="me")

    assert repo.all_settings() == {}
