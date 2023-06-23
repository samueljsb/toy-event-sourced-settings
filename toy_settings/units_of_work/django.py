from __future__ import annotations

from typing import Any

import attrs
from django.db import transaction
from typing_extensions import Self

from toy_settings.application import unit_of_work
from toy_settings.repositories.django import repo


@attrs.define
class DjangoUoW(unit_of_work.UnitOfWork):
    repo: repo.DjangoRepo

    committed: bool = False

    @classmethod
    def new(cls) -> Self:
        return cls(
            repo=repo.DjangoRepo(),
        )

    def __enter__(self) -> Self:
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self) -> None:
        transaction.commit()

    def rollback(self) -> None:
        transaction.rollback()
