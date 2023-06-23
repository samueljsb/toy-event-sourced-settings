from __future__ import annotations

import attrs

from toy_settings.application import unit_of_work
from toy_settings.domain import events
from toy_settings.repositories import memory


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
