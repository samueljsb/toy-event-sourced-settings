from __future__ import annotations

import datetime

import attrs

from . import events
from . import storage


@attrs.frozen
class AlreadySet(Exception):
    key: str


@attrs.frozen
class NotSet(Exception):
    key: str


@attrs.frozen
class ToySettings:
    repo: storage.Repository

    def set(
        self,
        key: str,
        value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> tuple[events.Event, ...]:
        """
        Create a new setting.

        Raises:
            AlreadySet: The setting already exists.
        """
        current_value = self.repo.current_value(key)
        if current_value is not None:
            raise AlreadySet(key)

        new_events = (
            events.Set(
                timestamp=timestamp,
                by=by,
                key=key,
                value=value,
            ),
        )

        for event in new_events:
            self.repo.record(event)

        return new_events

    def change(
        self,
        key: str,
        new_value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> tuple[events.Event, ...]:
        """
        Change the current value of a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        current_value = self.repo.current_value(key)
        if current_value is None:
            raise NotSet(key)

        new_events = (
            events.Changed(
                timestamp=timestamp,
                by=by,
                key=key,
                new_value=new_value,
            ),
        )

        for event in new_events:
            self.repo.record(event)

        return new_events

    def unset(
        self,
        key: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> tuple[events.Event, ...]:
        """
        Unset a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        current_value = self.repo.current_value(key)
        if current_value is None:
            raise NotSet(key)

        new_events = (
            events.Unset(
                timestamp=timestamp,
                by=by,
                key=key,
            ),
        )

        for event in new_events:
            self.repo.record(event)

        return new_events
