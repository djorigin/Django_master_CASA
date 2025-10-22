from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import MaintenanceRecord, MaintenanceType


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
