from __future__ import annotations

import datetime

import factory

from toy_settings.domain import events


class Event(factory.Factory):
    class Meta:
        model = events.Event
        abstract = True

    timestamp = factory.LazyFunction(datetime.datetime.now)
    by = "me"


class Set(Event):
    class Meta:
        model = events.Set

    key: str
    value: str


class Changed(Event):
    class Meta:
        model = events.Changed

    key: str
    new_value: str


class Unset(Event):
    class Meta:
        model = events.Unset

    key: str
