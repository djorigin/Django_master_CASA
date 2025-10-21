from django.urls import path

from .views import client_greeting, home

app_name = "core"

urlpatterns = [
    path("", home, name="index"),  # Changed name from 'home' to 'index' for consistency
    path("api/greeting/", client_greeting),
]
