from __future__ import annotations

import contextlib
import json
from typing import Any
from typing import Generator

from django import forms
from django import http
from django import urls
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views import generic
from tenacity import Retrying
from tenacity import retry_if_exception_type
from tenacity import wait_random_exponential

from .domain import services
from .domain import storage


# NOTE: this concern should usually live in the service layer with units of work, but we
# don't have any here (yet?)
@contextlib.contextmanager
def retry(max_wait_seconds: int) -> Generator[None, None, None]:
    for attempt in Retrying(
        retry=retry_if_exception_type(storage.StaleState),
        wait=wait_random_exponential(multiplier=0.1, max=max_wait_seconds),
    ):
        with attempt:
            yield


class Settings(generic.TemplateView):
    template_name = "settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = storage.get_repository()
        settings = repo.all_settings()
        context["settings"] = sorted(settings.items())

        return context


class SettingsJson(generic.View):
    def get(self, request: http.HttpRequest) -> http.HttpResponse:
        repo = storage.get_repository()
        settings = repo.all_settings()
        return http.HttpResponse(json.dumps(settings))


class SettingHistory(generic.TemplateView):
    template_name = "setting_history.html"

    def get_context_data(self, key: str, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = storage.get_repository()
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
        toy_settings = services.ToySettings.new()

        key = toy_settings.normalize_key(form.cleaned_data["key"])
        value = form.cleaned_data["value"]

        try:
            with retry(5):
                toy_settings.set(
                    key,
                    value,
                    timestamp=timezone.now(),
                    by="Some User",
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

        repo = storage.get_repository()
        current_value = repo.current_value(self.key)

        initial["key"] = self.key
        initial["value"] = current_value

        return initial

    def form_valid(self, form: ChangeSetting) -> HttpResponse:
        toy_settings = services.ToySettings.new()

        key = toy_settings.normalize_key(form.cleaned_data["key"])
        value = form.cleaned_data["value"]

        try:
            with retry(10):
                toy_settings.change(
                    key,
                    value,
                    timestamp=timezone.now(),
                    by="Some User",
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
        toy_settings = services.ToySettings.new()

        try:
            with retry(10):
                toy_settings.unset(
                    key,
                    timestamp=timezone.now(),
                    by="Some User",
                )
        except services.NotSet:
            messages.error(request, f"there is no {key!r} setting to unset")
        else:
            messages.success(request, f"{key!r} unset")

        return super().post(request, *args, **kwargs)
