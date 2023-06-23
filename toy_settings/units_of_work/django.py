from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from typing import Iterator

import attrs
from django.db import transaction
from typing_extensions import Self

from toy_settings.application import unit_of_work
from toy_settings.domain import events
from toy_settings.repositories.django import models
from toy_settings.repositories.django import repo


class DjangoCommitter(unit_of_work.Committer):
    @contextmanager
    def atomic(self) -> Iterator[None]:
        with transaction.atomic():
            yield

    def handle(self, event: events.Event) -> None:
        event_type, event_type_version = models.EVENT_TYPES[type(event)]
        models.Event.objects.create(
            event_type=event_type,
            event_type_version=event_type_version,
            timestamp=event.timestamp,
            key=event.key,
            payload=models.Event.payload_converter.dumps(event),
        )


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
