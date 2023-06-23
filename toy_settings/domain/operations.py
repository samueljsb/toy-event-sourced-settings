from __future__ import annotations

import datetime

import attrs

from . import events
from . import queries


@attrs.frozen
class AlreadySet(Exception):
    key: str


@attrs.frozen
class NotSet(Exception):
    key: str


@attrs.frozen
class ToySettings:
    state: queries.Repository

    def set(
        self,
        key: str,
        value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> events.Event:
        """
        Create a new setting.

        Raises:
            AlreadySet: The setting already exists.
        """
        current_value = self.state.current_value(key)
        if current_value is not None:
            raise AlreadySet(key)

        return events.Set(
            timestamp=timestamp,
            by=by,
            key=key,
            value=value,
        )

    def change(
        self,
        key: str,
        new_value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> events.Event:
        """
        Change the current value of a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        current_value = self.state.current_value(key)
        if current_value is None:
            raise NotSet(key)

        return events.Changed(
            timestamp=timestamp,
            by=by,
            key=key,
            new_value=new_value,
        )

    def unset(
        self,
        key: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> events.Event:
        """
        Unset a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        current_value = self.state.current_value(key)
        if current_value is None:
            raise NotSet(key)

        return events.Unset(
            timestamp=timestamp,
            by=by,
            key=key,
        )
