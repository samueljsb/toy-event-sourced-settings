from __future__ import annotations

import json
import os
import unittest.mock

import pytest
from django.utils import timezone
from django_webtest import DjangoTestApp
from django_webtest import DjangoWebtestResponse

from toy_settings import config
from toy_settings.domain import events

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture(autouse=True)
def temp_file_queries(tmp_path):
    with unittest.mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(tmp_path)}):
        yield


def _get_messages(response: DjangoWebtestResponse) -> list[tuple[str, str]]:
    return [
        (msg.level_tag, msg.message)
        for msg in response.context["messages"]._loaded_messages
    ]


def test_setting_history(django_app: DjangoTestApp):
    repo = config.get_repository()
    repo.record(
        events.Set(
            timestamp=timezone.now(),
            by="Some user",
            key="FOO",
            value="42",
        )
    )
    response = django_app.get("/history/FOO/")
    assert response.status_code == 200


def _set_setting(
    django_app: DjangoTestApp, key: str, value: str
) -> DjangoWebtestResponse:
    page = django_app.get("/set/")
    form = page.form
    form["key"] = key
    form["value"] = value
    return form.submit()


def test_settings_json(django_app: DjangoTestApp):
    _set_setting(django_app, "FOO", "42")
    _set_setting(django_app, "BAR", "something")
    _set_setting(django_app, "BAZ", "something else")

    response = django_app.get("/json/")

    assert json.loads(response.body) == {
        "FOO": "42",
        "BAR": "something",
        "BAZ": "something else",
    }


def test_set_new_setting(django_app: DjangoTestApp):
    response = _set_setting(django_app, "FOO", "42")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("success", "'FOO' set to '42'"),
    ]

    repo = config.get_repository()
    assert repo.all_settings() == {"FOO": "42"}


def test_new_setting_normalizes_key(django_app: DjangoTestApp):
    _set_setting(django_app, "foo-bar value", "42")

    repo = config.get_repository()
    assert repo.all_settings() == {"FOO_BAR_VALUE": "42"}


def test_cannot_set_new_setting_if_already_set(django_app: DjangoTestApp):
    # set the setting once
    _set_setting(django_app, "FOO", "42")

    # try to set it again
    response = _set_setting(django_app, "FOO", "43")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("danger", "'FOO' is already set"),
    ]


def _change_setting(
    django_app: DjangoTestApp, key: str, new_value: str
) -> DjangoWebtestResponse:
    page = django_app.get(f"/change/{key}/")
    form = page.form
    form["value"] = new_value
    return form.submit()


def test_change_setting(django_app: DjangoTestApp):
    # set the setting once
    _set_setting(django_app, "FOO", "42")

    # change the setting
    response = _change_setting(django_app, "FOO", "43")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("success", "'FOO' set to '43'"),
    ]

    repo = config.get_repository()
    assert repo.all_settings() == {"FOO": "43"}


def test_cannot_change_non_existent_setting(django_app: DjangoTestApp):
    # change a setting that hasn't been set yet
    response = _change_setting(django_app, "FOO", "43")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("danger", "there is no 'FOO' setting to change"),
    ]

    repo = config.get_repository()
    assert repo.all_settings() == {}


def _unset_setting(django_app: DjangoTestApp, key: str) -> DjangoWebtestResponse:
    return django_app.post(f"/unset/{key}/")


def test_unset_setting(django_app_factory):
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)

    # set the setting once
    _set_setting(django_app, "FOO", "42").follow()

    # unset the setting
    response = _unset_setting(django_app, "FOO")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("success", "'FOO' unset"),
    ]

    repo = config.get_repository()
    assert repo.all_settings() == {}


def test_cannot_unset_non_existent_setting(django_app_factory):
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)

    # try to unset a setting that hasn't been set yet
    response = _unset_setting(django_app, "FOO")

    assert response.status_code == 302
    assert response.location == "/"

    response = response.follow()
    assert response.status_code == 200
    assert _get_messages(response) == [
        ("danger", "there is no 'FOO' setting to unset"),
    ]

    repo = config.get_repository()
    assert repo.all_settings() == {}
