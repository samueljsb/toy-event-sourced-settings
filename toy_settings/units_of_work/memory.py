from __future__ import annotations

import attrs

from toy_settings.repositories import memory
from toy_settings.services import unit_of_work


@attrs.define
class MemoryUoW(unit_of_work.UnitOfWork):
    repo: memory.MemoryRepo

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
