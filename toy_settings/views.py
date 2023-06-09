from __future__ import annotations

import json
from typing import Any

from django import forms
from django import http
from django import urls
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views import generic
from tenacity import RetryError

from toy_settings import config

from .application import services

MAX_WAIT_SECONDS = 5


def normalize_key(key: str) -> str:
    return key.strip().replace(" ", "_").replace("-", "_").upper()


class Settings(generic.TemplateView):
    template_name = "settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = config.get_repository()
        settings = repo.all_settings()
        context["settings"] = sorted(settings.items())

        return context


class SettingsJson(generic.View):
    def get(self, request: http.HttpRequest) -> http.HttpResponse:
        repo = config.get_repository()
        settings = repo.all_settings()
        return http.HttpResponse(json.dumps(settings))


class SettingHistory(generic.TemplateView):
    template_name = "setting_history.html"

    def get_context_data(self, key: str, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = config.get_repository()
        context["key"] = key
        context["value"] = repo.current_value(key)
        events = repo.events_for_key(key)
        context["events"] = sorted(events, key=lambda e: e.timestamp, reverse=True)

        return context


class NewSettingForm(forms.Form):
    key = forms.CharField(required=True)
    value = forms.CharField(required=True)


class SetSetting(generic.FormView):
    template_name = "set_setting.html"
    form_class = NewSettingForm
    success_url = urls.reverse_lazy("settings")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        initial["key"] = self.request.GET.get("key")
        initial["value"] = self.request.GET.get("value")

        return initial

    def form_valid(self, form: NewSettingForm) -> HttpResponse:
        toy_settings = config.get_services()

        key = normalize_key(form.cleaned_data["key"])
        value = form.cleaned_data["value"]

        try:
            with toy_settings.retry(max_wait_seconds=MAX_WAIT_SECONDS):
                toy_settings.set(
                    key,
                    value,
                    timestamp=timezone.now(),
                    by="Some User",
                )
        except RetryError:  # pragma: no cover
            messages.error(
                self.request, "oh no! Something went wrong. Please try again."
            )
        except services.AlreadySet:
            messages.error(self.request, f"{key!r} is already set")
        else:
            messages.success(self.request, f"{key!r} set to {value!r}")

        return super().form_valid(form)


class ChangeSettingForm(forms.Form):
    key = forms.CharField(required=True, disabled=True)
    value = forms.CharField(required=True)


class ChangeSetting(generic.FormView):
    template_name = "set_setting.html"
    form_class = ChangeSettingForm
    success_url = urls.reverse_lazy("settings")

    def setup(
        self, request: http.HttpRequest, *args: Any, key: str, **kwargs: Any
    ) -> None:
        self.key = key

        return super().setup(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        repo = config.get_repository()
        current_value = repo.current_value(self.key)

        initial["key"] = self.key
        initial["value"] = current_value

        return initial

    def form_valid(self, form: ChangeSetting) -> HttpResponse:
        toy_settings = config.get_services()

        key = normalize_key(form.cleaned_data["key"])
        value = form.cleaned_data["value"]

        try:
            with toy_settings.retry(max_wait_seconds=MAX_WAIT_SECONDS):
                toy_settings.change(
                    key,
                    value,
                    timestamp=timezone.now(),
                    by="Some User",
                )
        except RetryError:  # pragma: no cover
            messages.error(
                self.request, "oh no! Something went wrong. Please try again."
            )
        except services.NotSet:
            messages.error(self.request, f"there is no {key!r} setting to change")
        else:
            messages.success(self.request, f"{key!r} set to {value!r}")

        return super().form_valid(form)


class UnsetSetting(generic.RedirectView):
    url = urls.reverse_lazy("settings")

    def post(
        self, request: http.HttpRequest, key: str, *args: Any, **kwargs: Any
    ) -> http.HttpResponse:
        toy_settings = config.get_services()

        try:
            with toy_settings.retry(max_wait_seconds=MAX_WAIT_SECONDS):
                toy_settings.unset(
                    key,
                    timestamp=timezone.now(),
                    by="Some User",
                )
        except RetryError:  # pragma: no cover
            messages.error(
                self.request, "oh no! Something went wrong. Please try again."
            )
        except services.NotSet:
            messages.error(request, f"there is no {key!r} setting to unset")
        else:
            messages.success(request, f"{key!r} unset")

        return super().post(request, *args, **kwargs)
