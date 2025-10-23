from django.urls import path

from . import crud_views

app_name = "flight_operations"

urlpatterns = [
    # Flight Operations Dashboard
    path("", crud_views.flight_operations_dashboard, name="dashboard"),
    # Mission CRUD
    path("missions/", crud_views.mission_list, name="mission_list"),
    path("missions/create/", crud_views.mission_create, name="mission_create"),
    path("missions/<int:pk>/", crud_views.mission_detail, name="mission_detail"),
    path("missions/<int:pk>/edit/", crud_views.mission_update, name="mission_update"),
    path("missions/<int:pk>/delete/", crud_views.mission_delete, name="mission_delete"),
    # Flight Plan CRUD
    path("flight-plans/", crud_views.flight_plan_list, name="flight_plan_list"),
    path(
        "flight-plans/create/", crud_views.flight_plan_create, name="flight_plan_create"
    ),
    path(
        "flight-plans/<int:pk>/",
        crud_views.flight_plan_detail,
        name="flight_plan_detail",
    ),
    path(
        "flight-plans/<int:pk>/edit/",
        crud_views.flight_plan_update,
        name="flight_plan_update",
    ),
    # Flight Log CRUD
    path("flight-logs/", crud_views.flight_log_list, name="flight_log_list"),
    path("flight-logs/create/", crud_views.flight_log_create, name="flight_log_create"),
    path(
        "flight-logs/<int:pk>/", crud_views.flight_log_detail, name="flight_log_detail"
    ),
    # Risk Register CRUD
    path("risk-register/", crud_views.risk_register_list, name="risk_register_list"),
    path(
        "risk-register/create/",
        crud_views.risk_register_create,
        name="risk_register_create",
    ),
    # Job Safety Assessment CRUD
    path("jsa/", crud_views.jsa_list, name="jsa_list"),
    path("jsa/create/", crud_views.jsa_create, name="jsa_create"),
    # AJAX Operations
    path(
        "ajax/mission/delete/<int:pk>/",
        crud_views.ajax_mission_delete,
        name="ajax_mission_delete",
    ),
    path(
        "ajax/flight-plan/delete/<int:pk>/",
        crud_views.ajax_flight_plan_delete,
        name="ajax_flight_plan_delete",
    ),
    path(
        "ajax/dashboard-stats/",
        crud_views.ajax_dashboard_stats,
        name="ajax_dashboard_stats",
    ),
]
