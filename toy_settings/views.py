from __future__ import annotations

import datetime
from typing import Any

from django import forms
from django import http
from django.http import HttpResponse
from django.views import generic

from . import repositories
from . import services


def _get_repo() -> repositories.Repository:
    return repositories.FileSystemRepo()


class Settings(generic.TemplateView):
    template_name = "settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = _get_repo()
        settings = repo.all_settings()
        context["settings"] = sorted(settings.items(), key=lambda kv: kv[0])

        return context


class SettingHistory(generic.TemplateView):
    template_name = "setting_history.html"

    def get_context_data(self, key: str, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = _get_repo()
        context["key"] = key
        context["value"] = repo.current_value(key)
        events = repo.events_for_key(key)
        context["events"] = sorted(events, key=lambda e: e.timestamp, reverse=True)

        return context


class SettingForm(forms.Form):
    key = forms.CharField(required=True)
    value = forms.CharField(required=True)


class SetSetting(generic.FormView):
    template_name = "set_setting.html"
    form_class = SettingForm
    success_url = "/"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        initial["key"] = self.request.GET.get("key")
        initial["value"] = self.request.GET.get("value")

        return initial

    def form_valid(self, form: SettingForm) -> HttpResponse:
        services.set(
            form.cleaned_data["key"],
            form.cleaned_data["value"],
            timestamp=datetime.datetime.now(),
            by="Some User",
            repo=_get_repo(),
        )
        return super().form_valid(form)


class UnsetSetting(generic.RedirectView):
    url = "/"

    def post(
        self, request: http.HttpRequest, key: str, *args: Any, **kwargs: Any
    ) -> http.HttpResponse:
        services.unset(
            key,
            timestamp=datetime.datetime.now(),
            by="Some User",
            repo=_get_repo(),
        )

        return super().post(request, *args, **kwargs)
