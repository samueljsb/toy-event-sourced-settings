from __future__ import annotations

import datetime
import uuid

import attrs

from . import events
from . import storage


@attrs.frozen
class ToySettings:
    repo: storage.Repository

    @classmethod
    def new(cls) -> ToySettings:
        return cls(
            repo=storage.get_repository(),
        )

    def _normalize_key(self, key: str) -> str:
        return key.strip().replace(" ", "_").replace("-", "_").upper()

    def set(
        self,
        key: str,
        value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> None:
        key = self._normalize_key(key)
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
