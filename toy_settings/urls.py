from django.urls import path

from . import views

urlpatterns = [
    path("", views.Settings.as_view(), name="settings"),
    path("set/", views.SetSetting.as_view(), name="set"),
    path("unset/<str:key>/", views.UnsetSetting.as_view(), name="unset"),
    path("history/<str:key>/", views.SettingHistory.as_view(), name="history"),
]
