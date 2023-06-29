from __future__ import annotations

from typing import Protocol


class Logger(Protocol):
    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        ...

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        ...
