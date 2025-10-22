from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import FlightLog, FlightPlan, Mission


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    """
    Admin interface for Mission Management
    """

    list_display = [
        "mission_id",
        "name",
        "mission_type",
        "client",
        "status_display",
        "priority_display",
        "planned_start_date",
        "mission_commander",
        "casa_status",
    ]
    list_filter = [
        "mission_type",
        "status",
        "priority",
        "casa_authorization_required",
        "risk_level",
        "risk_assessment_completed",
    ]
    search_fields = [
        "mission_id",
        "name",
        "client__company_name",
        "mission_commander__user__username",
        "description",
    ]
    date_hierarchy = "planned_start_date"

    fieldsets = (
        (
            "Mission Identification",
            {
                "fields": (
                    "mission_id",
                    "name",
                    "mission_type",
                    "description",
                )
            },
        ),
        (
            "Personnel & Client",
            {
                "fields": (
                    "client",
                    "mission_commander",
                )
            },
        ),
        (
            "Status & Priority",
            {
                "fields": (
                    "status",
                    "priority",
                )
            },
        ),
        (
            "Scheduling",
            {
                "fields": (
                    "planned_start_date",
                    "planned_end_date",
                    "actual_start_date",
                    "actual_end_date",
                )
            },
        ),
        (
            "CASA Compliance",
            {
                "fields": (
                    "casa_authorization_required",
                    "casa_authorization_reference",
                )
            },
        ),
        (
            "Risk Assessment",
            {
                "fields": (
                    "risk_assessment_completed",
                    "risk_level",
                )
            },
        ),
        (
            "Documentation",
            {"fields": ("briefing_notes",)},
        ),
    )

    readonly_fields = ["mission_id", "created_at", "updated_at"]

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "planning": "blue",
            "approved": "green",
            "active": "orange",
            "completed": "green",
            "cancelled": "red",
            "suspended": "red",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def priority_display(self, obj):
        """Display priority with color coding"""
        colors = {
            "low": "green",
            "medium": "orange",
            "high": "red",
            "critical": "darkred",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, "black"),
            obj.get_priority_display(),
        )

    priority_display.short_description = "Priority"

    def casa_status(self, obj):
        """Display CASA authorization status"""
        if obj.casa_authorization_required:
            if obj.casa_authorization_reference:
                return format_html('<span style="color: green;">✓ Authorized</span>')
            else:
                return format_html(
                    '<span style="color: red;">⚠ Authorization Required</span>'
                )
        else:
            return format_html('<span style="color: gray;">Not Required</span>')

    casa_status.short_description = "CASA Status"

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return (
            super()
            .get_queryset(request)
            .select_related("client", "mission_commander__user")
        )


@admin.register(FlightPlan)
class FlightPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for Flight Plan Management
    """

    list_display = [
        "flight_plan_id",
        "mission_link",
        "aircraft_link",
        "pilot_in_command",
        "flight_type",
        "status_display",
        "planned_departure_time",
        "compliance_status",
    ]
    list_filter = [
        "flight_type",
        "status",
        "airspace_coordination_required",
        "notam_checked",
        "planned_departure_time",
    ]
    search_fields = [
        "flight_plan_id",
        "mission__name",
        "aircraft__registration_mark",
        "pilot_in_command__user__username",
        "departure_location",
    ]
    date_hierarchy = "planned_departure_time"

    fieldsets = (
        (
            "Flight Plan Identification",
            {
                "fields": (
                    "flight_plan_id",
                    "mission",
                    "aircraft",
                    "flight_type",
                    "status",
                )
            },
        ),
        (
            "Crew",
            {
                "fields": (
                    "pilot_in_command",
                    "remote_pilot_observer",
                )
            },
        ),
        (
            "Location & Route",
            {
                "fields": (
                    "operational_area",
                    "departure_location",
                    "departure_latitude",
                    "departure_longitude",
                    "route_waypoints",
                )
            },
        ),
        (
            "Flight Parameters",
            {
                "fields": (
                    "planned_altitude_agl",
                    "maximum_range_from_pilot",
                )
            },
        ),
        (
            "Timing",
            {
                "fields": (
                    "planned_departure_time",
                    "estimated_flight_time",
                    "actual_departure_time",
                    "actual_landing_time",
                )
            },
        ),
        (
            "Weather & Conditions",
            {
                "fields": (
                    "weather_minimums",
                    "planned_weather_check_time",
                )
            },
        ),
        (
            "CASA Compliance",
            {
                "fields": (
                    "notam_checked",
                    "airspace_coordination_required",
                    "airspace_coordination_reference",
                )
            },
        ),
        (
            "Safety Procedures",
            {
                "fields": (
                    "emergency_procedures",
                    "lost_link_procedures",
                )
            },
        ),
    )

    readonly_fields = ["flight_plan_id", "created_at", "updated_at"]

    def mission_link(self, obj):
        """Create link to mission detail"""
        url = reverse("admin:flight_operations_mission_change", args=[obj.mission.pk])
        return format_html('<a href="{}">{}</a>', url, obj.mission.mission_id)

    mission_link.short_description = "Mission"
    mission_link.admin_order_field = "mission__mission_id"

    def aircraft_link(self, obj):
        """Create link to aircraft detail"""
        url = reverse("admin:aircraft_aircraft_change", args=[obj.aircraft.pk])
        return format_html('<a href="{}">{}</a>', url, obj.aircraft.registration_mark)

    aircraft_link.short_description = "Aircraft"
    aircraft_link.admin_order_field = "aircraft__registration_mark"

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "draft": "gray",
            "submitted": "blue",
            "approved": "green",
            "active": "orange",
            "completed": "green",
            "cancelled": "red",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def compliance_status(self, obj):
        """Display compliance status"""
        issues = []
        if (
            obj.airspace_coordination_required
            and not obj.airspace_coordination_reference
        ):
            issues.append("Airspace")
        if not obj.notam_checked:
            issues.append("NOTAM")

        if issues:
            return format_html(
                '<span style="color: red;">⚠ {}</span>', ", ".join(issues)
            )
        else:
            return format_html('<span style="color: green;">✓ Compliant</span>')

    compliance_status.short_description = "Compliance"

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "mission",
                "aircraft",
                "pilot_in_command__user",
                "remote_pilot_observer__user",
                "operational_area",
            )
        )


@admin.register(FlightLog)
class FlightLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Flight Log Management
    """

    list_display = [
        "log_id",
        "flight_plan_link",
        "aircraft_display",
        "takeoff_time",
        "flight_time_display",
        "log_entry_type",
        "objectives_achieved_display",
        "maintenance_required_display",
    ]
    list_filter = [
        "log_entry_type",
        "objectives_achieved",
        "maintenance_required",
        "takeoff_time",
    ]
    search_fields = [
        "log_id",
        "flight_plan__flight_plan_id",
        "flight_plan__aircraft__registration_mark",
        "flight_plan__pilot_in_command__user__username",
    ]
    date_hierarchy = "takeoff_time"

    fieldsets = (
        (
            "Log Identification",
            {
                "fields": (
                    "log_id",
                    "flight_plan",
                    "log_entry_type",
                )
            },
        ),
        (
            "Flight Performance",
            {
                "fields": (
                    "takeoff_time",
                    "landing_time",
                    "flight_time",
                    "maximum_altitude_achieved",
                    "maximum_range_achieved",
                )
            },
        ),
        (
            "Aircraft Performance",
            {
                "fields": (
                    "pre_flight_battery_voltage",
                    "post_flight_battery_voltage",
                )
            },
        ),
        (
            "Weather Conditions",
            {
                "fields": (
                    "wind_speed_takeoff",
                    "wind_direction_takeoff",
                    "temperature_celsius",
                    "visibility_meters",
                )
            },
        ),
        (
            "Flight Assessment",
            {
                "fields": (
                    "objectives_achieved",
                    "technical_issues",
                    "weather_issues",
                    "operational_notes",
                    "lessons_learned",
                )
            },
        ),
        (
            "Pilot Performance",
            {"fields": ("pilot_performance_notes",)},
        ),
        (
            "Compliance & Data",
            {
                "fields": (
                    "regulatory_compliance_notes",
                    "data_collected",
                    "file_references",
                )
            },
        ),
        (
            "Maintenance",
            {
                "fields": (
                    "maintenance_required",
                    "maintenance_notes",
                )
            },
        ),
    )

    readonly_fields = ["log_id", "created_at", "updated_at"]

    def flight_plan_link(self, obj):
        """Create link to flight plan detail"""
        url = reverse(
            "admin:flight_operations_flightplan_change", args=[obj.flight_plan.pk]
        )
        return format_html('<a href="{}">{}</a>', url, obj.flight_plan.flight_plan_id)

    flight_plan_link.short_description = "Flight Plan"
    flight_plan_link.admin_order_field = "flight_plan__flight_plan_id"

    def aircraft_display(self, obj):
        """Display aircraft registration"""
        return obj.flight_plan.aircraft.registration_mark

    aircraft_display.short_description = "Aircraft"
    aircraft_display.admin_order_field = "flight_plan__aircraft__registration_mark"

    def flight_time_display(self, obj):
        """Display flight time in hours and minutes"""
        total_seconds = int(obj.flight_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    flight_time_display.short_description = "Flight Time"
    flight_time_display.admin_order_field = "flight_time"

    def objectives_achieved_display(self, obj):
        """Display objectives status with icon"""
        if obj.objectives_achieved:
            return format_html('<span style="color: green;">✓ Yes</span>')
        else:
            return format_html('<span style="color: red;">✗ No</span>')

    objectives_achieved_display.short_description = "Objectives"

    def maintenance_required_display(self, obj):
        """Display maintenance requirement with color"""
        if obj.maintenance_required:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ Required</span>'
            )
        else:
            return format_html('<span style="color: green;">✓ Not Required</span>')

    maintenance_required_display.short_description = "Maintenance"

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "flight_plan__aircraft", "flight_plan__pilot_in_command__user"
            )
        )
