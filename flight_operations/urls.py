from django.urls import path

from . import views

app_name = "flight_operations"

urlpatterns = [
    # Dashboard
    path("", views.flight_operations_dashboard, name="dashboard"),
    # Missions
    path("missions/", views.MissionListView.as_view(), name="mission_list"),
    path(
        "missions/<str:mission_id>/",
        views.MissionDetailView.as_view(),
        name="mission_detail",
    ),
    # Flight Plans
    path("flight-plans/", views.FlightPlanListView.as_view(), name="flightplan_list"),
    path(
        "flight-plans/<str:flight_plan_id>/",
        views.FlightPlanDetailView.as_view(),
        name="flightplan_detail",
    ),
    # Flight Logs
    path("flight-logs/", views.FlightLogListView.as_view(), name="flightlog_list"),
    path(
        "flight-logs/<str:log_id>/",
        views.FlightLogDetailView.as_view(),
        name="flightlog_detail",
    ),
    # API Endpoints
    path(
        "api/missions/<str:mission_id>/",
        views.mission_status_api,
        name="mission_status_api",
    ),
]
