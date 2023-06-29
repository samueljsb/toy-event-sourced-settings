from __future__ import annotations

import structlog


class StructlogLogger:
    def __init__(self) -> None:
        self.logger = structlog.get_logger()

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        self.logger.error(msg, *args, **kwargs)
