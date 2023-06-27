from __future__ import annotations

import datetime

import factory

from toy_settings.domain import events


class Event(factory.Factory):
    class Meta:
        model = events.Event
        abstract = True

    timestamp = factory.LazyFunction(datetime.datetime.now)


class Set(Event):
    class Meta:
        model = events.Set

    key: str
    value: str

    by = "me"


class Changed(Event):
    class Meta:
        model = events.Changed

    key: str
    new_value: str

    by = "me"


class Unset(Event):
    class Meta:
        model = events.Unset

    key: str

    by = "me"
