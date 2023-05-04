import datetime

from toy_settings import events
from toy_settings import services
from toy_settings.repositories import MemoryRepo


def _set_event(key: str, value: str, id: str) -> events.Set:
    return events.Set(
        id=id,
        timestamp=datetime.datetime.now(),
        by="me",
        key=key,
        value=value,
    )


def _unset_event(key: str, id: str) -> events.Unset:
    return events.Unset(
        id=id,
        timestamp=datetime.datetime.now(),
        by="me",
        key=key,
    )


def test_set_normalizes_key():
    repo = MemoryRepo()

    services.set(
        "foo",
        "42",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )

    assert repo.all_settings() == {"FOO": "42"}


def test_set_updates_value():
    repo = MemoryRepo()

    services.set(
        "FOO",
        "42",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )
    services.set(
        "foo",
        "43",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )

    assert repo.all_settings() == {"FOO": "43"}


def test_unset_removes_value():
    repo = MemoryRepo(
        [
            _set_event("FOO", "42", id="1"),
        ]
    )

    services.unset(
        "FOO",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )

    assert repo.all_settings() == {}


def test_unset_already_unset():
    repo = MemoryRepo(
        [
            _set_event("FOO", "42", id="1"),
            _unset_event("FOO", id="2"),
        ]
    )

    # check doing it twice has no effect
    services.unset(
        "FOO",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )

    assert repo.all_settings() == {}


def test_unset_never_set():
    repo = MemoryRepo([])

    services.unset(
        "FOO",
        timestamp=datetime.datetime.now(),
        by="me",
        repo=repo,
    )

    assert repo.all_settings() == {}
