from __future__ import annotations

import attrs

from toy_settings.domain import events
from toy_settings.domain import projections
from toy_settings.domain import queries


@attrs.frozen
class MemoryRepo(queries.Repository):
    history: list[events.Event] = attrs.field(factory=list)

    def events_for_key(self, key: str) -> list[events.Event]:  # pragma: no cover
        return sorted(
            (event for event in self.history if event.key == key),
            key=lambda e: e.timestamp,
        )

    def get_setting(self, key: str) -> projections.Setting:
        return projections.current_settings(
            sorted(
                self.history,
                key=lambda e: e.timestamp,
            )
        )[key]

    def current_value(self, key: str) -> str | None:  # pragma: no cover
        return self.all_settings().get(key, None)

    def all_settings(self) -> dict[str, str]:  # pragma: no cover
        return {
            key: setting.value
            for key, setting in projections.current_settings(
                sorted(
                    self.history,
                    key=lambda e: e.timestamp,
                )
            ).items()
            if setting.value is not None
        }
