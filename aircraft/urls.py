from django.urls import path
from . import views

app_name = 'aircraft'

urlpatterns = [
    path('', views.AircraftListView.as_view(), name='aircraft_list'),
    path('<str:registration_mark>/', views.AircraftDetailView.as_view(), name='aircraft_detail'),
    path('api/status/<str:registration_mark>/', views.aircraft_status_api, name='aircraft_status_api'),
    path('dashboard/compliance/', views.aircraft_compliance_dashboard, name='compliance_dashboard'),
]