from __future__ import annotations

import contextlib
import datetime
from typing import Generator

import attrs
from tenacity import Retrying
from tenacity import retry_if_exception_type
from tenacity import wait_random_exponential

from toy_settings.domain import services
from toy_settings.domain import storage


@attrs.frozen
class AlreadySet(Exception):
    key: str


@attrs.frozen
class NotSet(Exception):
    key: str


@attrs.frozen
class ToySettings:
    repo: storage.Repository
    max_wait_seconds: int

    @classmethod
    def new(cls, max_wait_seconds: int = 0) -> ToySettings:
        return cls(
            repo=storage.get_repository(),
            max_wait_seconds=max_wait_seconds,
        )

    @contextlib.contextmanager
    def retry(self) -> Generator[None, None, None]:
        for attempt in Retrying(
            retry=retry_if_exception_type(storage.StaleState),
            wait=wait_random_exponential(multiplier=0.1, max=self.max_wait_seconds),
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
        domain = services.ToySettings(repo=self.repo)
        with self.retry():
            try:
                domain.set(
                    key,
                    value,
                    timestamp=timestamp,
                    by=by,
                )
            except services.AlreadySet as exc:
                raise AlreadySet(key) from exc

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
        domain = services.ToySettings(repo=self.repo)
        with self.retry():
            try:
                domain.change(
                    key,
                    new_value,
                    timestamp=timestamp,
                    by=by,
                )
            except services.NotSet as exc:
                raise NotSet(key) from exc

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
        domain = services.ToySettings(repo=self.repo)
        with self.retry():
            try:
                domain.unset(
                    key,
                    timestamp=timestamp,
                    by=by,
                )
            except services.NotSet as exc:
                raise NotSet(key) from exc
