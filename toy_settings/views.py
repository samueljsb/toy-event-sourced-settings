from __future__ import annotations

import datetime
from typing import Any

from django import forms
from django import http
from django import urls
from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from . import services
from . import storage


class Settings(generic.TemplateView):
    template_name = "settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        repo = storage.get_repository()
        settings = repo.all_settings()
        context["settings"] = sorted(settings.items())

        return context


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


class SettingForm(forms.Form):
    key = forms.CharField(required=True)
    value = forms.CharField(required=True)


class SetSetting(generic.FormView):
    template_name = "set_setting.html"
    form_class = SettingForm
    success_url = urls.reverse_lazy("settings")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        initial["key"] = self.request.GET.get("key")
        initial["value"] = self.request.GET.get("value")

        return initial

    def form_valid(self, form: SettingForm) -> HttpResponse:
        toy_settings = services.ToySettings.new()

        key = toy_settings.normalize_key(form.cleaned_data["key"])
        value = form.cleaned_data["value"]

        try:
            toy_settings.set(
                key,
                value,
                timestamp=datetime.datetime.now(),
                by="Some User",
            )
        except services.AlreadySet:
            messages.error(self.request, f"{key!r} is already set")
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
            toy_settings.unset(
                key,
                timestamp=datetime.datetime.now(),
                by="Some User",
            )
        except services.NotSet:
            messages.error(request, f"there is no {key!r} setting to unset")
        else:
            messages.success(request, f"{key!r} unset")

        return super().post(request, *args, **kwargs)
