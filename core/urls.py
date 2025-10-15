from django.urls import path
from .views import home, client_greeting

urlpatterns = [
    path('', home, name='home'),
    path('api/greeting/', client_greeting),
]

