from __future__ import annotations

import abc
from contextlib import contextmanager
from typing import Iterator

from django.utils.module_loading import import_string

from toy_settings.domain import events

DEFAULT_TOY_SETTINGS_COMMITTER = "toy_settings.units_of_work.django.DjangoCommitter"


def get_committer() -> Committer:
    return import_string(DEFAULT_TOY_SETTINGS_COMMITTER)()


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
