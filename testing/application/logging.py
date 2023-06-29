from __future__ import annotations

import attrs

from toy_settings.application.logging import Logger


@attrs.define
class MemoryLogger(Logger):
    logged: list[
        tuple[str, object, tuple[object, ...], dict[str, object]]
    ] = attrs.field(factory=list)

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        self.logged.append(("info", msg, args, kwargs))

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        self.logged.append(("error", msg, args, kwargs))
