from __future__ import annotations

import abc
from typing import Any

from django.utils.module_loading import import_string
from typing_extensions import Self

from toy_settings.domain import queries

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
