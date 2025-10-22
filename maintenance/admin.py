from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    MaintenanceRecord,
    MaintenanceType,
    RPASMaintenanceEntry,
    RPASTechnicalLogPartA,
    RPASTechnicalLogPartB,
)


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for Maintenance Type Management
    """

    list_display = [
        "name",
        "type_category",
        "priority_display",
        "casa_required",
        "licensed_engineer_required",
        "frequency_summary",
    ]
    list_filter = [
        "type_category",
        "priority",
        "casa_required",
        "licensed_engineer_required",
    ]
    search_fields = ["name", "description", "reference_manual"]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "type_category", "priority", "description")},
        ),
        (
            "Scheduling",
            {"fields": ("frequency_hours", "frequency_days", "frequency_cycles")},
        ),
        (
            "CASA Compliance",
            {
                "fields": (
                    "casa_required",
                    "licensed_engineer_required",
                    "casa_form_required",
                )
            },
        ),
        ("Documentation", {"fields": ("reference_manual",)}),
    )

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

    def frequency_summary(self, obj):
        """Display frequency requirements summary"""
        frequencies = []
        if obj.frequency_hours:
            frequencies.append(f"{obj.frequency_hours}h")
        if obj.frequency_days:
            frequencies.append(f"{obj.frequency_days}d")
        if obj.frequency_cycles:
            frequencies.append(f"{obj.frequency_cycles}c")

        return " / ".join(frequencies) if frequencies else "As Required"

    frequency_summary.short_description = "Frequency"


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for Maintenance Record Management
    """

    list_display = [
        "maintenance_id",
        "aircraft_link",
        "maintenance_type",
        "scheduled_date",
        "status_display",
        "completion_status_display",
        "performed_by",
        "overdue_status",
    ]
    list_filter = [
        "status",
        "completion_status",
        "maintenance_type__type_category",
        "maintenance_type__priority",
        "scheduled_date",
        "casa_form_completed",
    ]
    search_fields = [
        "maintenance_id",
        "aircraft__registration_mark",
        "performed_by__user__username",
        "work_performed",
    ]
    date_hierarchy = "scheduled_date"

    fieldsets = (
        (
            "Identification",
            {"fields": ("maintenance_id", "aircraft", "maintenance_type")},
        ),
        ("Personnel", {"fields": ("performed_by", "supervised_by")}),
        (
            "Scheduling",
            {"fields": ("scheduled_date", "started_date", "completed_date")},
        ),
        (
            "Aircraft State",
            {"fields": ("pre_maintenance_hours", "post_maintenance_hours")},
        ),
        ("Status", {"fields": ("status", "completion_status")}),
        (
            "Work Details",
            {
                "fields": (
                    "work_performed",
                    "parts_used",
                    "defects_found",
                    "corrective_actions",
                )
            },
        ),
        (
            "CASA Compliance",
            {"fields": ("casa_form_completed", "return_to_service_authorization")},
        ),
        (
            "Cost & Follow-up",
            {
                "fields": (
                    "labor_hours",
                    "parts_cost",
                    "next_maintenance_due",
                    "followup_required",
                )
            },
        ),
    )

    readonly_fields = ["maintenance_id", "created_at", "updated_at"]

    def aircraft_link(self, obj):
        """Create link to aircraft detail"""
        url = reverse("admin:aircraft_aircraft_change", args=[obj.aircraft.pk])
        return format_html('<a href="{}">{}</a>', url, obj.aircraft.registration_mark)

    aircraft_link.short_description = "Aircraft"
    aircraft_link.admin_order_field = "aircraft__registration_mark"

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "scheduled": "blue",
            "in_progress": "orange",
            "completed": "green",
            "deferred": "orange",
            "cancelled": "red",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def completion_status_display(self, obj):
        """Display completion status with color coding"""
        if not obj.completion_status:
            return "-"

        colors = {
            "satisfactory": "green",
            "unsatisfactory": "red",
            "partial": "orange",
            "requires_followup": "orange",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.completion_status, "black"),
            obj.get_completion_status_display(),
        )

    completion_status_display.short_description = "Completion"

    def overdue_status(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            days_overdue = (timezone.now().date() - obj.scheduled_date).days
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ {} days overdue</span>',
                days_overdue,
            )
        elif obj.status == "completed":
            return format_html('<span style="color: green;">✓ Completed</span>')
        else:
            days_until = (obj.scheduled_date - timezone.now().date()).days
            if days_until <= 7:
                return format_html(
                    '<span style="color: orange;">⚠ Due in {} days</span>', days_until
                )
            else:
                return format_html('<span style="color: green;">On Schedule</span>')

    overdue_status.short_description = "Schedule Status"

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "aircraft",
                "maintenance_type",
                "performed_by__user",
                "supervised_by__user",
            )
        )


class RPASMaintenanceEntryInline(admin.TabularInline):
    """Inline admin for RPAS Maintenance Entries"""

    model = RPASMaintenanceEntry
    extra = 1
    fields = [
        "item_description",
        "maintenance_record",
        "due_date_tts",
        "completed_date_arn",
        "defect_category",
    ]
    readonly_fields = ["maintenance_status"]


@admin.register(RPASTechnicalLogPartA)
class RPASTechnicalLogPartAAdmin(admin.ModelAdmin):
    """
    Admin interface for RPAS Technical Log Part A
    Matches company standard form layout
    """

    list_display = [
        "aircraft",
        "rpa_type_model",
        "current_status",
        "has_major_defects_display",
        "has_minor_defects_display",
        "created_at",
        "created_by",
    ]

    list_filter = [
        "current_status",
        "aircraft__aircraft_type__manufacturer",
        "aircraft__aircraft_type__model",
        "created_at",
    ]

    search_fields = [
        "aircraft__registration_mark",
        "aircraft__serial_number",
        "rpa_type_model",
    ]

    fieldsets = (
        (
            "RPA Identification",
            {
                "fields": (
                    "aircraft",
                    "rpa_type_model",
                    "max_gross_weight",
                    "date_of_registration_expiry",
                ),
                "description": "Basic RPA identification matching Technical Log Part A",
            },
        ),
        (
            "Maintenance Schedule",
            {
                "fields": ("maintenance_schedule_reference",),
                "description": "Reference to manufacturer maintenance system",
            },
        ),
        (
            "Part 101 MOC Certification",
            {
                "fields": (
                    "part_101_moc_issued_by",
                    "part_101_moc_issued_on",
                    "part_101_moc_signed_by",
                ),
                "description": "CASA Part 101 Method of Compliance certification",
            },
        ),
        (
            "Defects Tracking",
            {
                "fields": (
                    "major_defects_notes",
                    "minor_defects_notes",
                    "current_status",
                ),
                "description": "Major and minor defects as per RPAS Technical Log requirements",
            },
        ),
        ("Administrative", {"fields": ("created_by",), "classes": ("collapse",)}),
    )

    readonly_fields = ["rpa_type_model", "max_gross_weight"]
    inlines = [RPASMaintenanceEntryInline]

    def has_major_defects_display(self, obj):
        """Display major defects status"""
        if obj.has_major_defects:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ YES</span>'
            )
        return format_html('<span style="color: green;">✓ NO</span>')

    has_major_defects_display.short_description = "Major Defects"

    def has_minor_defects_display(self, obj):
        """Display minor defects status"""
        if obj.has_minor_defects:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ YES</span>'
            )
        return format_html('<span style="color: green;">✓ NO</span>')

    has_minor_defects_display.short_description = "Minor Defects"


class RPASTechnicalLogPartBInline(admin.TabularInline):
    """Inline admin for Part B daily logs"""

    model = RPASTechnicalLogPartB
    extra = 0
    fields = [
        "date",
        "flight_time",
        "progressive_total_hrs",
        "progressive_total_min",
        "inspection_satisfactory",
        "inspector",
    ]
    readonly_fields = ["progressive_total_hrs", "progressive_total_min"]


@admin.register(RPASTechnicalLogPartB)
class RPASTechnicalLogPartBAdmin(admin.ModelAdmin):
    """
    Admin interface for RPAS Technical Log Part B
    Daily inspection and time tracking
    """

    list_display = [
        "aircraft_display",
        "date",
        "flight_time",
        "total_time_formatted",
        "inspection_satisfactory_display",
        "inspector",
        "signature_type",
    ]

    list_filter = [
        "inspection_satisfactory",
        "signature_type",
        "date",
        "technical_log_part_a__aircraft__aircraft_type__manufacturer",
    ]

    search_fields = [
        "technical_log_part_a__aircraft__registration_mark",
        "inspector__user__first_name",
        "inspector__user__last_name",
        "signature_identifier",
    ]

    fieldsets = (
        (
            "Daily Inspection",
            {
                "fields": (
                    "technical_log_part_a",
                    "date",
                    "daily_inspection_certification",
                    "inspection_satisfactory",
                    "defects_found",
                )
            },
        ),
        (
            "Authorization",
            {"fields": ("signature_type", "signature_identifier", "inspector")},
        ),
        (
            "RPA Time in Service",
            {
                "fields": (
                    "flight_time",
                    "progressive_total_hrs",
                    "progressive_total_min",
                ),
                "description": "Flight time tracking with automatic progressive totals",
            },
        ),
        (
            "Integration",
            {
                "fields": ("linked_flight_logs",),
                "classes": ("collapse",),
                "description": "Links to flight operations system",
            },
        ),
        ("Notes", {"fields": ("daily_notes",), "classes": ("collapse",)}),
    )

    readonly_fields = ["progressive_total_hrs", "progressive_total_min"]
    filter_horizontal = ["linked_flight_logs"]

    def aircraft_display(self, obj):
        """Display aircraft registration"""
        return obj.aircraft.registration_mark

    aircraft_display.short_description = "Aircraft"

    def inspection_satisfactory_display(self, obj):
        """Display inspection status"""
        if obj.inspection_satisfactory:
            return format_html('<span style="color: green;">✓ Satisfactory</span>')
        else:
            return format_html('<span style="color: red;">✗ Unsatisfactory</span>')

    inspection_satisfactory_display.short_description = "Inspection"


@admin.register(RPASMaintenanceEntry)
class RPASMaintenanceEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for RPAS Maintenance Entry bridge records
    """

    list_display = [
        "item_description",
        "technical_log_aircraft",
        "maintenance_record",
        "defect_category",
        "due_date_tts",
        "is_completed_display",
    ]

    list_filter = [
        "defect_category",
        "maintenance_record__status",
        "technical_log_part_a__aircraft__aircraft_type__manufacturer",
    ]

    search_fields = [
        "item_description",
        "maintenance_record__maintenance_id",
        "technical_log_part_a__aircraft__registration_mark",
    ]

    fieldsets = (
        (
            "RPAS Technical Log Integration",
            {"fields": ("technical_log_part_a", "item_description", "defect_category")},
        ),
        (
            "Maintenance Record Link",
            {
                "fields": ("maintenance_record", "rpas_specific_notes"),
                "description": "Links to existing maintenance system",
            },
        ),
        (
            "RPAS Specific Data",
            {
                "fields": (
                    "due_date_tts",
                    "completed_date_arn",
                    "completed_by_name",
                    "completed_by_arn",
                ),
                "description": "Additional fields required for RPAS Technical Log compliance",
            },
        ),
    )

    def technical_log_aircraft(self, obj):
        """Display aircraft from technical log"""
        return obj.technical_log_part_a.aircraft.registration_mark

    technical_log_aircraft.short_description = "Aircraft"

    def is_completed_display(self, obj):
        """Display completion status"""
        if obj.is_completed:
            return format_html('<span style="color: green;">✓ Completed</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')

    is_completed_display.short_description = "Status"
