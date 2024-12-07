from django.urls import path

from . import views

app_name='lotto'
urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("stat", views.StatView.as_view(), name="stat"),
    path("stat/<int:mode>", views.StatView.as_view(), name="stat_mode")
]