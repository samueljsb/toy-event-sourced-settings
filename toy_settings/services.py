from __future__ import annotations

import datetime
import uuid

from . import events
from . import projections
from . import storage


def set(
    key: str,
    value: str,
    *,
    timestamp: datetime.datetime,
    by: str,
    repo: storage.Repository,
) -> None:
    key = projections.normalize_key(key)
    repo.record(
        events.Set(
            id=uuid.uuid4().hex,
            timestamp=timestamp,
            by=by,
            key=key,
            value=value,
        )
    )


def unset(
    key: str, *, timestamp: datetime.datetime, by: str, repo: storage.Repository
) -> None:
    repo.record(
        events.Unset(
            id=uuid.uuid4().hex,
            timestamp=timestamp,
            by=by,
            key=key,
        )
    )
