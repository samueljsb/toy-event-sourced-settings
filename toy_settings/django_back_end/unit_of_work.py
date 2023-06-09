from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from django.db import IntegrityError
from django.db import transaction

from toy_settings.application import unit_of_work
from toy_settings.domain import events

from . import models


class DjangoCommitter(unit_of_work.Committer):
    @contextmanager
    def atomic(self) -> Iterator[None]:
        with transaction.atomic():
            yield

    def handle(self, event: events.Event) -> None:
        event_type, event_type_version = models.EVENT_TYPES[type(event)]
        new_event = models.Event.objects.create(
            event_type=event_type,
            event_type_version=event_type_version,
            timestamp=event.timestamp,
            key=event.key,
            payload=models.Event.payload_converter.dumps(event),
        )
        try:
            models.Sequence.objects.create(
                event=new_event,
                key=event.key,
                index=event.index,
            )
        except IntegrityError as exc:
            raise unit_of_work.StaleState from exc
