from django.urls import path
from .views import home, client_greeting

app_name = 'core'

urlpatterns = [
    path('', home, name='index'),  # Changed name from 'home' to 'index' for consistency
    path('api/greeting/', client_greeting),
]

