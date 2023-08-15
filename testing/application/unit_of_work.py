from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import attrs

from toy_settings.application import unit_of_work
from toy_settings.domain import events


@attrs.define
class MemoryCommitter(unit_of_work.Committer):
    committed: list[events.Event] = attrs.field(init=False, factory=list)
    uncommitted_events: list[events.Event] = attrs.field(init=False)

    @contextmanager
    def atomic(self) -> Iterator[None]:
        self.uncommitted_events: list[events.Event] = []
        yield
        self.committed.extend(self.uncommitted_events)
        del self.uncommitted_events

    def handle(self, event: events.Event) -> None:
        self.uncommitted_events.append(event)
