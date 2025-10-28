from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import FlightLog, FlightPlan, Mission


class MissionListView(LoginRequiredMixin, ListView):
    """
    List view for missions with status and priority filtering
    """

    model = Mission
    template_name = "flight_operations/mission_list.html"
    context_object_name = "missions"
    paginate_by = 20

    def get_queryset(self):
        return Mission.objects.select_related(
            "client", "mission_commander__user"
        ).order_by("-planned_start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add summary statistics
        queryset = self.get_queryset()
        context["total_missions"] = queryset.count()
        context["active_missions"] = queryset.filter(status="active").count()
        context["pending_missions"] = queryset.filter(status="planning").count()
        context["completed_missions"] = queryset.filter(status="completed").count()

        return context


class MissionDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for individual missions
    """

    model = Mission
    template_name = "flight_operations/mission_detail.html"
    context_object_name = "mission"
    slug_field = "mission_id"
    slug_url_kwarg = "mission_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related flight plans from both aircraft and drone sets
        aircraft_plans = self.object.aircraftflightplan_set.all()
        drone_plans = self.object.droneflightplan_set.all()

        # Combine and order by planned departure time
        all_plans = list(aircraft_plans) + list(drone_plans)
        all_plans.sort(
            key=lambda x: (
                x.planned_departure_time if x.planned_departure_time else timezone.now()
            )
        )

        context["flight_plans"] = all_plans
        return context


class FlightPlanListView(LoginRequiredMixin, ListView):
    """
    List view for flight plans with mission and aircraft details
    """

    model = FlightPlan
    template_name = "flight_operations/flightplan_list.html"
    context_object_name = "flight_plans"
    paginate_by = 20

    def get_queryset(self):
        return FlightPlan.objects.select_related(
            "mission", "aircraft", "pilot_in_command__user"
        ).order_by("-planned_departure_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add summary statistics
        queryset = self.get_queryset()
        context["total_plans"] = queryset.count()
        context["approved_plans"] = queryset.filter(status="approved").count()
        context["active_plans"] = queryset.filter(status="active").count()
        context["completed_plans"] = queryset.filter(status="completed").count()

        return context


class FlightPlanDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for individual flight plans
    """

    model = FlightPlan
    template_name = "flight_operations/flightplan_detail.html"
    context_object_name = "flight_plan"
    slug_field = "flight_plan_id"
    slug_url_kwarg = "flight_plan_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add flight log if exists
        try:
            context["flight_log"] = self.object.flightlog
        except FlightLog.DoesNotExist:
            context["flight_log"] = None
        return context


class FlightLogListView(LoginRequiredMixin, ListView):
    """
    List view for flight logs with performance data
    """

    model = FlightLog
    template_name = "flight_operations/flightlog_list.html"
    context_object_name = "flight_logs"
    paginate_by = 20

    def get_queryset(self):
        return FlightLog.objects.select_related(
            "flight_plan__aircraft", "flight_plan__pilot_in_command__user"
        ).order_by("-takeoff_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add summary statistics
        queryset = self.get_queryset()
        context["total_flights"] = queryset.count()
        context["total_flight_hours"] = sum(log.total_flight_hours for log in queryset)
        context["maintenance_required"] = queryset.filter(
            maintenance_required=True
        ).count()
        context["objectives_achieved"] = queryset.filter(
            objectives_achieved=True
        ).count()

        return context


class FlightLogDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for individual flight logs
    """

    model = FlightLog
    template_name = "flight_operations/flightlog_detail.html"
    context_object_name = "flight_log"
    slug_field = "log_id"
    slug_url_kwarg = "log_id"


@login_required
def mission_status_api(request, mission_id):
    """
    API endpoint for mission status information
    """
    try:
        mission = Mission.objects.select_related("client", "mission_commander").get(
            mission_id=mission_id
        )

        return JsonResponse(
            {
                "mission_id": mission.mission_id,
                "name": mission.name,
                "status": mission.status,
                "priority": mission.priority,
                "is_active": mission.is_active,
                "planned_start": mission.planned_start_date.isoformat(),
                "planned_end": mission.planned_end_date.isoformat(),
                "client": mission.client.company_name,
                "casa_authorization_required": mission.casa_authorization_required,
            }
        )
    except Mission.DoesNotExist:
        return JsonResponse({"error": "Mission not found"}, status=404)


@login_required
def flight_operations_dashboard(request):
    """
    Dashboard view showing flight operations overview
    """
    # Current active operations
    active_missions = Mission.objects.filter(status="active").select_related(
        "client", "mission_commander__user"
    )

    # Upcoming flights (next 7 days)
    next_week = timezone.now() + timezone.timedelta(days=7)
    upcoming_flights = FlightPlan.objects.filter(
        planned_departure_time__gte=timezone.now(),
        planned_departure_time__lte=next_week,
        status__in=["approved", "active"],
    ).select_related("mission", "aircraft", "pilot_in_command__user")

    # Recent flight logs (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_logs = FlightLog.objects.filter(
        takeoff_time__gte=thirty_days_ago
    ).select_related("flight_plan__aircraft", "flight_plan__pilot_in_command__user")

    # Statistics
    stats = {
        "active_missions": active_missions.count(),
        "upcoming_flights": upcoming_flights.count(),
        "recent_flights": recent_logs.count(),
        "total_flight_hours": sum(log.total_flight_hours for log in recent_logs),
        "maintenance_required": recent_logs.filter(maintenance_required=True).count(),
    }

    # Mission types breakdown
    mission_types = {}
    for mission in Mission.objects.all():
        mission_type = mission.get_mission_type_display()
        mission_types[mission_type] = mission_types.get(mission_type, 0) + 1

    context = {
        "stats": stats,
        "active_missions": active_missions[:5],  # Latest 5
        "upcoming_flights": upcoming_flights[:5],  # Next 5
        "recent_logs": recent_logs[:5],  # Latest 5
        "mission_types": mission_types,
    }

    return render(request, "flight_operations/dashboard.html", context)
