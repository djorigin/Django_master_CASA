from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Aircraft, AircraftType


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for CASA Aircraft Type Management
    """

    list_display = [
        "name",
        "manufacturer",
        "model",
        "category",
        "operation_type",
        "maximum_takeoff_weight",
        "casa_compliant_status",
    ]
    list_filter = [
        "category",
        "operation_type",
        "excluded_category_compliant",
        "manufacturer",
    ]
    search_fields = ["name", "manufacturer", "model", "casa_type_certificate"]
    fieldsets = (
        (
            "Aircraft Type Information",
            {"fields": ("name", "manufacturer", "model", "category", "operation_type")},
        ),
        (
            "Technical Specifications",
            {
                "fields": (
                    "maximum_takeoff_weight",
                    "maximum_operating_height",
                    "maximum_speed",
                )
            },
        ),
        (
            "CASA Compliance",
            {"fields": ("casa_type_certificate", "excluded_category_compliant")},
        ),
        (
            "Documentation Requirements",
            {"fields": ("flight_manual_required", "maintenance_manual_required")},
        ),
    )
    readonly_fields = ["excluded_category_compliant"]

    def casa_compliant_status(self, obj):
        """Display CASA compliance status with color coding"""
        if obj.excluded_category_compliant:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Excluded Category</span>'
            )
        elif obj.casa_type_certificate:
            return format_html(
                '<span style="color: blue; font-weight: bold;">✓ Type Certified</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;">⚠ Requires Certificate</span>'
            )

    casa_compliant_status.short_description = "CASA Status"


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    """
    Admin interface for Individual Aircraft Management
    """

    list_display = [
        "registration_mark",
        "aircraft_type_display",
        "owner",
        "status",
        "operational_status",
        "airworthiness_status",
        "maintenance_status_display",
    ]
    list_filter = [
        "status",
        "aircraft_type__category",
        "aircraft_type__operation_type",
        "aircraft_type__manufacturer",
    ]
    search_fields = [
        "registration_mark",
        "serial_number",
        "owner__company_name",
        "aircraft_type__manufacturer",
        "aircraft_type__model",
    ]
    date_hierarchy = "registration_date"

    fieldsets = (
        (
            "Registration Information",
            {
                "fields": (
                    "registration_mark",
                    "aircraft_type",
                    "serial_number",
                    "year_manufactured",
                    "registration_date",
                )
            },
        ),
        ("Ownership & Operation", {"fields": ("owner", "operator")}),
        (
            "Status & Compliance",
            {
                "fields": (
                    "status",
                    "airworthiness_valid_until",
                    "insurance_valid_until",
                )
            },
        ),
        (
            "Maintenance",
            {
                "fields": (
                    "last_maintenance_check",
                    "next_maintenance_due",
                    "current_flight_hours",
                    "maximum_flight_hours",
                )
            },
        ),
        ("Documentation", {"fields": ("flight_manual_reference", "notes")}),
    )

    readonly_fields = ["created_at", "updated_at"]

    def aircraft_type_display(self, obj):
        """Display aircraft type with manufacturer and model"""
        return f"{obj.aircraft_type.manufacturer} {obj.aircraft_type.model}"

    aircraft_type_display.short_description = "Aircraft Type"
    aircraft_type_display.admin_order_field = "aircraft_type__manufacturer"

    def operational_status(self, obj):
        """Display operational status with color coding"""
        if obj.is_operational:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Operational</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Not Operational</span>'
            )

    operational_status.short_description = "Operational"

    def airworthiness_status(self, obj):
        """Display airworthiness status with expiry information"""
        if obj.is_airworthy:
            if obj.airworthiness_valid_until:
                days_remaining = (
                    obj.airworthiness_valid_until - timezone.now().date()
                ).days
                if days_remaining <= 30:
                    return format_html(
                        '<span style="color: orange;">⚠ Expires in {} days</span>',
                        days_remaining,
                    )
                else:
                    return format_html(
                        '<span style="color: green;">✓ Valid until {}</span>',
                        obj.airworthiness_valid_until.strftime("%d/%m/%Y"),
                    )
            else:
                return format_html(
                    '<span style="color: green;">✓ Excluded Category</span>'
                )
        else:
            return format_html('<span style="color: red;">✗ Expired</span>')

    airworthiness_status.short_description = "Airworthiness"

    def maintenance_status_display(self, obj):
        """Display maintenance status with color coding"""
        status = obj.maintenance_status
        if status == "current":
            return format_html('<span style="color: green;">✓ Current</span>')
        elif status == "due_soon":
            return format_html('<span style="color: orange;">⚠ Due Soon</span>')
        elif status == "overdue":
            return format_html('<span style="color: red;">✗ Overdue</span>')
        else:
            return format_html('<span style="color: gray;">? Unknown</span>')

    maintenance_status_display.short_description = "Maintenance"

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return (
            super()
            .get_queryset(request)
            .select_related("aircraft_type", "owner", "operator")
        )
