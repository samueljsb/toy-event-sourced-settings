from django.urls import path

from . import views

urlpatterns = [
    path("", views.Settings.as_view()),
    path("set/", views.SetSetting.as_view()),
    path("unset/<str:key>/", views.UnsetSetting.as_view()),
    path("history/<str:key>/", views.SettingHistory.as_view()),
]
