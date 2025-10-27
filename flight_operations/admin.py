from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AircraftFlightPlan,
    DroneFlightPlan,
    FlightLog,
    FlightPlan,
    JobSafetyAssessment,
    Mission,
    MissionAssignment,
    RiskRegister,
)


class MissionAssignmentInline(admin.TabularInline):
    """Inline for mission crew assignments"""

    model = MissionAssignment
    extra = 0
    fields = ['role', 'pilot', 'staff_member', 'is_primary', 'notes']
    autocomplete_fields = ['pilot', 'staff_member']


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
        "overall_risk_level",
        "risk_assessment_required",
        "jsa_required",
    ]
    search_fields = [
        "mission_id",
        "name",
        "client__company_name",
        "mission_commander__user__username",
        "description",
    ]
    date_hierarchy = "planned_start_date"
    inlines = [MissionAssignmentInline]

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


@admin.register(RiskRegister)
class RiskRegisterAdmin(admin.ModelAdmin):
    """
    Admin interface for Risk Register Management
    """

    list_display = [
        "reference_number",
        "mission",
        "hazard",
        "risk_description",
        "risk_level_display",
        "risk_accepted",
        "risk_owner",
    ]

    list_filter = [
        "risk_level",
        "risk_accepted",
        "initial_likelihood",
        "initial_consequence",
        "mission__mission_type",
    ]

    search_fields = [
        "reference_number",
        "hazard",
        "risk_description",
        "mission__name",
        "mission__mission_id",
    ]

    fieldsets = (
        (
            "Risk Identification",
            {
                "fields": (
                    "reference_number",
                    "mission",
                    "date_entered",
                    "hazard",
                    "risk_description",
                )
            },
        ),
        (
            "Risk Assessment",
            {
                "fields": (
                    "initial_likelihood",
                    "initial_consequence",
                    "initial_risk_rating",
                    "existing_controls",
                )
            },
        ),
        (
            "Risk Treatment",
            {
                "fields": (
                    "additional_controls",
                    "residual_likelihood",
                    "residual_consequence",
                    "residual_risk_rating",
                )
            },
        ),
        (
            "Risk Management",
            {
                "fields": (
                    "risk_level",
                    "acceptance_level",
                    "risk_owner",
                    "review_due_date",
                    "actions_required",
                )
            },
        ),
        (
            "Risk Acceptance",
            {"fields": ("risk_accepted", "accepted_by", "accepted_date")},
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = (
        "initial_risk_rating",
        "residual_risk_rating",
        "risk_level",
        "acceptance_level",
        "created_at",
        "updated_at",
    )

    def risk_level_display(self, obj):
        """Display risk level with color coding"""
        colors = {"low": "green", "medium": "orange", "high": "red"}
        color = colors.get(obj.risk_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.risk_level.upper(),
        )

    risk_level_display.short_description = "Risk Level"


@admin.register(JobSafetyAssessment)
class JobSafetyAssessmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Job Safety Assessment Management
    """

    list_display = [
        "jsa_id",
        "mission",
        "operation_type",
        "flight_authorized",
        "section1_approved",
        "section2_approved",
    ]

    list_filter = [
        "operation_type",
        "flight_authorized",
        "airspace_class",
        "sop_adequate",
        "preliminary_assessment_accurate",
    ]

    search_fields = [
        "jsa_id",
        "mission__name",
        "mission__mission_id",
        "operation_description",
        "hazards_identified",
    ]

    fieldsets = (
        ("JSA Identification", {"fields": ("jsa_id", "mission", "operation_type")}),
        (
            "Operating Area",
            {
                "fields": (
                    "operating_area_map",
                    "airspace_class",
                    "maximum_operating_height_agl",
                )
            },
        ),
        (
            "Risk Assessment",
            {"fields": ("hazards_addressed", "sop_adequate", "unmitigated_hazards")},
        ),
        (
            "Assessment Validation",
            {
                "fields": (
                    "preliminary_assessment_accurate",
                    "assessment_changes",
                    "additional_operating_restrictions",
                )
            },
        ),
        (
            "Authorization",
            {
                "fields": (
                    "official_authorization",
                    "flight_authorized",
                    "authorized_date",
                    "authorized_by",
                )
            },
        ),
        (
            "Approvals",
            {
                "fields": (
                    "section1_approval_signature",
                    "section1_approval_date",
                    "section2_approval_signature",
                    "section2_approval_date",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("jsa_id", "created_at", "updated_at")

    def section1_approved(self, obj):
        """Display Section 1 approval status"""
        if obj.section1_approval_signature and obj.section1_approval_date:
            return format_html('<span style="color: green;">✓ Approved</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')

    section1_approved.short_description = "Section 1"

    def section2_approved(self, obj):
        """Display Section 2 approval status"""
        if obj.section2_approval_signature and obj.section2_approval_date:
            return format_html('<span style="color: green;">✓ Approved</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')

    section2_approved.short_description = "Section 2"


@admin.register(MissionAssignment)
class MissionAssignmentAdmin(admin.ModelAdmin):
    """Admin for mission crew assignments"""

    list_display = [
        'mission',
        'assigned_person_name',
        'role',
        'is_primary',
        'created_at',
    ]
    list_filter = ['role', 'is_primary']
    search_fields = [
        'mission__mission_id',
        'mission__name',
        'pilot__user__username',
        'staff_member__user__username',
    ]
    autocomplete_fields = ['mission', 'pilot', 'staff_member']


@admin.register(AircraftFlightPlan)
class AircraftFlightPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for Aircraft Flight Plan Management
    """

    list_display = [
        'flight_plan_id',
        'mission',
        'aircraft',
        'pilot_in_command',
        'status_display',
        'flight_type',
        'departure_airport',
        'arrival_airport',
        'planned_departure_time',
    ]

    list_filter = [
        'status',
        'flight_type',
        'flight_rules',
        'created_at',
    ]

    search_fields = [
        'flight_plan_id',
        'mission__name',
        'mission__mission_id',
        'aircraft__registration_mark',
        'pilot_in_command__user__username',
        'departure_airport',
        'arrival_airport',
    ]

    fieldsets = (
        (
            'Flight Plan Information',
            {
                'fields': (
                    'flight_plan_id',
                    'mission',
                    'status',
                    'flight_type',
                    'flight_rules',
                )
            },
        ),
        (
            'Aircraft and Crew',
            {
                'fields': (
                    'aircraft',
                    'pilot_in_command',
                    'co_pilot',
                    'passenger_count',
                )
            },
        ),
        (
            'Route and Navigation',
            {
                'fields': (
                    'departure_airport',
                    'arrival_airport',
                    'alternate_airport',
                    'route',
                    'cruise_altitude',
                )
            },
        ),
        (
            'Timing',
            {
                'fields': (
                    'planned_departure_time',
                    'planned_arrival_time',
                    'estimated_flight_time',
                    'actual_departure_time',
                    'actual_arrival_time',
                )
            },
        ),
        (
            'Performance and Loading',
            {
                'fields': (
                    'fuel_required',
                    'fuel_loaded',
                    'payload_weight',
                )
            },
        ),
        (
            'Weather and Safety',
            {
                'fields': (
                    'weather_conditions',
                    'weather_minimums',
                    'special_instructions',
                    'emergency_procedures',
                )
            },
        ),
        (
            'Regulatory Compliance',
            {
                'fields': (
                    'notam_checked',
                    'airspace_coordination_required',
                    'airspace_coordination_reference',
                    'atc_clearance',
                )
            },
        ),
    )

    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'planned_departure_time'
    autocomplete_fields = ['mission', 'aircraft', 'pilot_in_command', 'co_pilot']

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'draft': 'orange',
            'submitted': 'blue',
            'approved': 'green',
            'active': 'purple',
            'completed': 'gray',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display(),
        )

    status_display.short_description = 'Status'


@admin.register(DroneFlightPlan)
class DroneFlightPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for Drone Flight Plan Management
    """

    list_display = [
        'flight_plan_id',
        'mission',
        'drone',
        'remote_pilot',
        'status_display',
        'flight_type',
        'maximum_altitude_agl',
        'planned_departure_time',
    ]

    list_filter = [
        'status',
        'flight_type',
        'autonomous_mode',
        'no_fly_zones_checked',
        'created_at',
    ]

    search_fields = [
        'flight_plan_id',
        'mission__name',
        'mission__mission_id',
        'drone__registration_mark',
        'remote_pilot__user__username',
        'takeoff_location',
        'landing_location',
    ]

    fieldsets = (
        (
            'Flight Plan Information',
            {
                'fields': (
                    'flight_plan_id',
                    'mission',
                    'status',
                    'flight_type',
                )
            },
        ),
        (
            'Drone and Crew',
            {
                'fields': (
                    'drone',
                    'remote_pilot',
                    'visual_observer',
                )
            },
        ),
        (
            'Operating Area',
            {
                'fields': (
                    'operational_area',
                    'takeoff_location',
                    'landing_location',
                    'operating_area_coordinates',
                    'maximum_altitude_agl',
                    'maximum_range_from_pilot',
                )
            },
        ),
        (
            'Timing',
            {
                'fields': (
                    'planned_departure_time',
                    'planned_arrival_time',
                    'estimated_flight_time',
                    'actual_departure_time',
                    'actual_arrival_time',
                )
            },
        ),
        (
            'Drone Performance',
            {
                'fields': (
                    'battery_capacity',
                    'estimated_battery_consumption',
                    'payload_description',
                )
            },
        ),
        (
            'Automated Flight Features',
            {
                'fields': (
                    'waypoints',
                    'autonomous_mode',
                    'return_to_home_altitude',
                )
            },
        ),
        (
            'Weather and Safety',
            {
                'fields': (
                    'weather_conditions',
                    'weather_minimums',
                    'special_instructions',
                    'emergency_procedures',
                    'lost_link_procedures',
                )
            },
        ),
        (
            'Regulatory Compliance',
            {
                'fields': (
                    'casa_approval_number',
                    'airspace_approval',
                    'notam_checked',
                    'airspace_coordination_required',
                    'airspace_coordination_reference',
                    'no_fly_zones_checked',
                )
            },
        ),
    )

    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'planned_departure_time'
    autocomplete_fields = [
        'mission',
        'drone',
        'remote_pilot',
        'visual_observer',
        'operational_area',
    ]

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'draft': 'orange',
            'submitted': 'blue',
            'approved': 'green',
            'active': 'purple',
            'completed': 'gray',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display(),
        )

    status_display.short_description = 'Status'
