from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("", views.Settings.as_view(), name="settings"),
    path("set/", views.SetSetting.as_view(), name="set"),
    path("change/<str:key>/", views.ChangeSetting.as_view(), name="change"),
    path("unset/<str:key>/", views.UnsetSetting.as_view(), name="unset"),
    path("history/<str:key>/", views.SettingHistory.as_view(), name="history"),
    path("json/", views.SettingsJson.as_view(), name="json"),
]
