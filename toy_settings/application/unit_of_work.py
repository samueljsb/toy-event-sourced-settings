from __future__ import annotations

import abc
from contextlib import contextmanager
from typing import Any
from typing import Iterator

from django.utils.module_loading import import_string
from typing_extensions import Self

from toy_settings.domain import events
from toy_settings.domain import queries


@contextmanager
def commit_on_success(committer: Committer) -> Iterator[list[events.Event]]:
    new_events: list[events.Event] = []
    yield new_events
    with committer.atomic():
        for event in new_events:
            committer.handle(event)


class StaleState(Exception):
    """
    An event could not be handled because the state has changed.
    """


class Committer(abc.ABC):
    @contextmanager
    @abc.abstractmethod
    def atomic(self) -> Iterator[None]:
        """Apply handled events atomically.

        Raises:
            StaleState: The state has changed and committing is no longer safe.
        """
        ...

    @abc.abstractmethod
    def handle(self, event: events.Event) -> None:
        """Handle a new event.

        Raises:
            StaleState: The state has changed and handling is no longer safe.
        """
        ...


DEFAULT_TOY_SETTINGS_UOW_PATH = "toy_settings.units_of_work.django.DjangoUoW"


def get_uow() -> UnitOfWork:
    return import_string(DEFAULT_TOY_SETTINGS_UOW_PATH).new()


class UnitOfWork(abc.ABC):
    repo: queries.Repository

    @classmethod
    @abc.abstractmethod
    def new(cls) -> Self:
        ...

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        ...

    @abc.abstractmethod
    def rollback(self) -> None:
        ...
