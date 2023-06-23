from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import attrs

from toy_settings.application import unit_of_work
from toy_settings.domain import events
from toy_settings.repositories import memory


@attrs.define
class MemoryCommitter(unit_of_work.Committer):
    history: list[events.Event] = attrs.field(factory=list)

    @contextmanager
    def atomic(self) -> Iterator[None]:
        self.uncommitted_events: list[events.Event] = []
        yield
        self.history.extend(self.uncommitted_events)
        del self.uncommitted_events

    def handle(self, event: events.Event) -> None:
        self.uncommitted_events.append(event)


@attrs.define
class MemoryUoW(unit_of_work.UnitOfWork):
    repo: memory.MemoryRepo
    history: list[events.Event] = attrs.field(factory=list)

    committed: bool = False

    @classmethod
    def new(cls) -> MemoryUoW:
        return cls(
            repo=memory.MemoryRepo(),
        )

    def __enter__(self) -> MemoryUoW:
        self.committed = False
        return super().__enter__()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass
