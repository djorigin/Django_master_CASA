from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import IncidentType, IncidentReport


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for Incident Type Management
    """
    list_display = [
        'name',
        'category',
        'severity_display',
        'casa_reportable_display',
        'reporting_timeframe_display',
        'investigation_required'
    ]
    list_filter = [
        'category',
        'severity',
        'casa_reportable',
        'immediate_notification_required',
        'investigation_required',
        'grounding_required'
    ]
    search_fields = [
        'name',
        'description',
        'casa_reference'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'category',
                'severity',
                'description'
            )
        }),
        ('CASA Reporting Requirements', {
            'fields': (
                'casa_reportable',
                'reporting_timeframe_hours',
                'immediate_notification_required'
            )
        }),
        ('Investigation & Response', {
            'fields': (
                'investigation_required',
                'grounding_required'
            )
        }),
        ('Documentation', {
            'fields': (
                'casa_reference',
            )
        })
    )

    def severity_display(self, obj):
        """Display severity with color coding"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severity, 'black'),
            obj.get_severity_display()
        )
    severity_display.short_description = 'Severity'

    def casa_reportable_display(self, obj):
        """Display CASA reportable status with icon"""
        if obj.casa_reportable:
            color = 'red' if obj.immediate_notification_required else 'orange'
            icon = '⚠⚠' if obj.immediate_notification_required else '⚠'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} Yes</span>',
                color, icon
            )
        else:
            return format_html('<span style="color: green;">✓ No</span>')
    casa_reportable_display.short_description = 'CASA Reportable'

    def reporting_timeframe_display(self, obj):
        """Display reporting timeframe"""
        if obj.casa_reportable and obj.reporting_timeframe_hours:
            return f"{obj.reporting_timeframe_hours}h"
        elif obj.immediate_notification_required:
            return "Immediate"
        else:
            return "-"
    reporting_timeframe_display.short_description = 'Reporting Time'


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    """
    Admin interface for Incident Report Management
    """
    list_display = [
        'incident_id',
        'incident_type',
        'incident_date',
        'aircraft_link',
        'pilot_in_command',
        'status_display',
        'casa_status_display',
        'investigation_status'
    ]
    list_filter = [
        'status',
        'incident_type__category',
        'incident_type__severity',
        'casa_reported',
        'investigation_completed',
        'weather_conditions',
        'flight_phase'
    ]
    search_fields = [
        'incident_id',
        'aircraft__registration_mark',
        'pilot_in_command__user__username',
        'location_description',
        'summary'
    ]
    date_hierarchy = 'incident_date'
    
    fieldsets = (
        ('Incident Identification', {
            'fields': (
                'incident_id',
                'incident_type',
                'status'
            )
        }),
        ('People & Assets', {
            'fields': (
                'aircraft',
                'pilot_in_command',
                'reported_by'
            )
        }),
        ('When & Where', {
            'fields': (
                'incident_date',
                'location_description',
                'latitude',
                'longitude'
            )
        }),
        ('Flight Details', {
            'fields': (
                'flight_phase',
                'flight_hours_on_aircraft'
            )
        }),
        ('Environmental Conditions', {
            'fields': (
                'weather_conditions',
                'wind_speed_knots',
                'visibility_meters'
            )
        }),
        ('Incident Description', {
            'fields': (
                'summary',
                'detailed_description'
            )
        }),
        ('Damage & Impact', {
            'fields': (
                'aircraft_damage',
                'property_damage',
                'injuries'
            )
        }),
        ('Analysis', {
            'fields': (
                'contributing_factors',
                'immediate_causes'
            )
        }),
        ('Actions Taken', {
            'fields': (
                'immediate_actions',
                'preventive_actions'
            )
        }),
        ('CASA Reporting', {
            'fields': (
                'casa_reported',
                'casa_report_date',
                'casa_reference_number'
            )
        }),
        ('Investigation', {
            'fields': (
                'investigation_completed',
                'investigation_findings',
                'investigation_completed_date'
            )
        }),
        ('Follow-up', {
            'fields': (
                'follow_up_required',
                'follow_up_actions'
            )
        })
    )
    
    readonly_fields = ['incident_id', 'created_at', 'updated_at']

    def aircraft_link(self, obj):
        """Create link to aircraft detail"""
        if obj.aircraft:
            url = reverse('admin:aircraft_aircraft_change', args=[obj.aircraft.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.aircraft.registration_mark
            )
        return "-"
    aircraft_link.short_description = 'Aircraft'
    aircraft_link.admin_order_field = 'aircraft__registration_mark'

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'under_investigation': 'orange',
            'casa_reported': 'purple',
            'closed': 'green',
            'reopened': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def casa_status_display(self, obj):
        """Display CASA reporting status"""
        if not obj.is_casa_reportable:
            return format_html('<span style="color: gray;">Not Required</span>')
        
        if obj.casa_reported:
            return format_html(
                '<span style="color: green;">✓ Reported {}</span>',
                obj.casa_report_date.strftime('%d/%m/%Y') if obj.casa_report_date else ''
            )
        elif obj.is_reporting_overdue:
            return format_html('<span style="color: red; font-weight: bold;">⚠ OVERDUE</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Required</span>')
    casa_status_display.short_description = 'CASA Status'

    def investigation_status(self, obj):
        """Display investigation status"""
        if not obj.incident_type.investigation_required:
            return format_html('<span style="color: gray;">Not Required</span>')
        
        if obj.investigation_completed:
            return format_html(
                '<span style="color: green;">✓ Complete</span>'
            )
        elif obj.status == 'under_investigation':
            return format_html('<span style="color: orange;">In Progress</span>')
        else:
            return format_html('<span style="color: red;">Pending</span>')
    investigation_status.short_description = 'Investigation'

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return super().get_queryset(request).select_related(
            'incident_type',
            'aircraft',
            'pilot_in_command__user',
            'reported_by'
        )
