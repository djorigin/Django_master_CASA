from django.urls import path

from . import crud_views, views

app_name = "aircraft"

urlpatterns = [
    # Dashboard
    path("", crud_views.aircraft_dashboard, name="dashboard"),
    # Aircraft Type URLs
    path("types/", crud_views.aircraft_type_list, name="aircraft_type_list"),
    path("types/create/", crud_views.aircraft_type_create, name="aircraft_type_create"),
    path(
        "types/<int:pk>/", crud_views.aircraft_type_detail, name="aircraft_type_detail"
    ),
    path(
        "types/<int:pk>/update/",
        crud_views.aircraft_type_update,
        name="aircraft_type_update",
    ),
    path(
        "types/<int:pk>/delete/",
        crud_views.aircraft_type_delete,
        name="aircraft_type_delete",
    ),
    # Aircraft URLs
    path("aircraft/", crud_views.aircraft_list, name="aircraft_list"),
    path("aircraft/create/", crud_views.aircraft_create, name="aircraft_create"),
    path("aircraft/<int:pk>/", crud_views.aircraft_detail, name="aircraft_detail"),
    path(
        "aircraft/<int:pk>/update/", crud_views.aircraft_update, name="aircraft_update"
    ),
    path(
        "aircraft/<int:pk>/delete/", crud_views.aircraft_delete, name="aircraft_delete"
    ),
    # Legacy API URLs (keeping for backward compatibility)
    path(
        "api/<str:registration_mark>/",
        views.AircraftDetailView.as_view(),
        name="aircraft_detail_api",
    ),
    path(
        "api/status/<str:registration_mark>/",
        views.aircraft_status_api,
        name="aircraft_status_api",
    ),
    path(
        "dashboard/compliance/",
        views.aircraft_compliance_dashboard,
        name="compliance_dashboard",
    ),
]
