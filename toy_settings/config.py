from __future__ import annotations

from .application.logging import Logger
from .application.services import ToySettings
from .application.unit_of_work import Committer
from .django_back_end.queries import DjangoRepo
from .django_back_end.unit_of_work import DjangoCommitter
from .domain.queries import Repository
from .logging import StructlogLogger


def get_repository() -> Repository:
    return DjangoRepo()


def get_committer() -> Committer:
    return DjangoCommitter()


def get_services() -> ToySettings:
    return ToySettings(
        state=get_repository(),
        committer=get_committer(),
        logger=get_logger(),
    )


def get_logger() -> Logger:
    return StructlogLogger()
