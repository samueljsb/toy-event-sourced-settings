from __future__ import annotations

from .application.services import ToySettings
from .application.unit_of_work import Committer
from .django_back_end.queries import DjangoRepo
from .django_back_end.unit_of_work import DjangoCommitter
from .domain.queries import Repository


def get_repository() -> Repository:
    return DjangoRepo()


def get_committer() -> Committer:
    return DjangoCommitter()


def get_services(max_wait_seconds: int) -> ToySettings:
    return ToySettings(
        state=get_repository(),
        committer=get_committer(),
        max_wait_seconds=max_wait_seconds,
    )
