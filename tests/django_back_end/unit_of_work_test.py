from __future__ import annotations

import pytest
from django.utils import timezone

from testing.domain import factories
from toy_settings.application import unit_of_work
from toy_settings.django_back_end.unit_of_work import DjangoCommitter

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize(
    "indexes",
    (
        pytest.param((1, 1), id="duplicate"),
        pytest.param((2, 1), id="out-of-order"),
    ),
)
def test_non_monotonic_insert_raises_StaleState(indexes):
    committer = DjangoCommitter()

    # set a setting
    committer.handle(
        factories.Set(key="FOO", value="42", timestamp=timezone.now(), index=0)
    )

    # two processes attempt to change the setting...
    # ... the first succeeds
    committer.handle(
        factories.Changed(
            key="FOO", new_value="43", timestamp=timezone.now(), index=indexes[0]
        )
    )

    # ... the second fails
    with pytest.raises(unit_of_work.StaleState):
        committer.handle(
            factories.Changed(
                key="FOO", new_value="99", timestamp=timezone.now(), index=indexes[1]
            )
        )
