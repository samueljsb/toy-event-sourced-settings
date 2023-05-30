from __future__ import annotations

import datetime
import uuid

import attrs

from . import events
from . import projections
from . import storage


@attrs.frozen
class ToySettings:
    repo: storage.Repository

    @classmethod
    def new(cls) -> ToySettings:
        return cls(
            repo=storage.get_repository(),
        )

    def set(
        self,
        key: str,
        value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> None:
        key = projections.normalize_key(key)
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
        self.repo.record(
            events.Unset(
                id=uuid.uuid4().hex,
                timestamp=timestamp,
                by=by,
                key=key,
            )
        )
