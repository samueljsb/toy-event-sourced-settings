from __future__ import annotations

from .application.unit_of_work import Committer
from .domain.queries import Repository
from .repositories.django.repo import DjangoRepo
from .units_of_work.django import DjangoCommitter


def get_repository() -> Repository:
    return DjangoRepo()


def get_committer() -> Committer:
    return DjangoCommitter()
