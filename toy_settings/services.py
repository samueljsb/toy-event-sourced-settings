from __future__ import annotations

import datetime
import uuid

import attrs

from . import events
from . import projections
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

    @classmethod
    def new(cls) -> ToySettings:
        return cls(
            repo=storage.get_repository(),
        )

    def normalize_key(self, key: str) -> str:
        return key.strip().replace(" ", "_").replace("-", "_").upper()

    def set(
        self,
        key: str,
        value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> None:
        """
        Create a new setting.

        Raises:
            AlreadySet: The setting already exists.
        """
        history = self.repo.events_for_key(key)
        current_value = projections.current_value(key, history)
        if current_value is not None:
            raise AlreadySet(key)

        self.repo.record(
            events.Set(
                id=uuid.uuid4().hex,
                timestamp=timestamp,
                by=by,
                key=key,
                value=value,
            )
        )

    def unset(
        self,
        key: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> None:
        """
        Unset a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        history = self.repo.events_for_key(key)
        current_value = projections.current_value(key, history)
        if current_value is None:
            raise NotSet(key)

        self.repo.record(
            events.Unset(
                id=uuid.uuid4().hex,
                timestamp=timestamp,
                by=by,
                key=key,
            )
        )
