from __future__ import annotations

import contextlib
import datetime
from typing import Generator

import attrs
from tenacity import Retrying
from tenacity import retry_if_exception_type
from tenacity import wait_random_exponential

from toy_settings.domain import operations
from toy_settings.domain import queries

from . import logging
from . import unit_of_work


@attrs.frozen
class AlreadySet(Exception):
    key: str


@attrs.frozen
class NotSet(Exception):
    key: str


@attrs.frozen
class ToySettings:
    state: queries.Repository
    committer: unit_of_work.Committer
    logger: logging.Logger

    @contextlib.contextmanager
    def retry(self, max_wait_seconds: int) -> Generator[None, None, None]:
        for attempt in Retrying(
            retry=retry_if_exception_type(unit_of_work.StaleState),
            wait=wait_random_exponential(multiplier=0.1, max=max_wait_seconds),
        ):
            with attempt:
                yield

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
        with unit_of_work.commit_on_success(self.committer) as new_events:
            domain = operations.ToySettings(state=self.state)
            try:
                new_event = domain.set(
                    key,
                    value,
                    timestamp=timestamp,
                    by=by,
                )
            except operations.AlreadySet as exc:
                raise AlreadySet(key) from exc
            else:
                new_events.append(new_event)

    def change(
        self,
        key: str,
        new_value: str,
        *,
        timestamp: datetime.datetime,
        by: str,
    ) -> None:
        """
        Change the current value of a setting.

        Raises:
            NotSet: There is no setting for this key.
        """
        with unit_of_work.commit_on_success(self.committer) as new_events:
            domain = operations.ToySettings(state=self.state)
            try:
                new_event = domain.change(
                    key,
                    new_value,
                    timestamp=timestamp,
                    by=by,
                )
            except operations.NotSet as exc:
                raise NotSet(key) from exc
            else:
                new_events.append(new_event)

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
        with unit_of_work.commit_on_success(self.committer) as new_events:
            domain = operations.ToySettings(state=self.state)
            try:
                new_event = domain.unset(
                    key,
                    timestamp=timestamp,
                    by=by,
                )
            except operations.NotSet as exc:
                raise NotSet(key) from exc
            else:
                new_events.append(new_event)
