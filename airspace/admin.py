from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import AirspaceClass, OperationalArea


@admin.register(AirspaceClass)
class AirspaceClassAdmin(admin.ModelAdmin):
    """
    Admin interface for Airspace Class Management
    """
    list_display = [
        'airspace_class',
        'name',
        'authorization_level_display',
        'maximum_height_agl',
        'excluded_category_allowed',
        'pilot_license_required'
    ]
    list_filter = [
        'authorization_level',
        'excluded_category_allowed',
        'pilot_license_required'
    ]
    search_fields = [
        'name',
        'description',
        'casa_regulation_reference'
    ]
    fieldsets = (
        ('Airspace Classification', {
            'fields': (
                'airspace_class',
                'name',
                'description'
            )
        }),
        ('RPA Operation Requirements', {
            'fields': (
                'authorization_level',
                'maximum_height_agl',
                'excluded_category_allowed',
                'pilot_license_required'
            )
        }),
        ('CASA References', {
            'fields': (
                'casa_regulation_reference',
            )
        })
    )

    def authorization_level_display(self, obj):
        """Display authorization level with color coding"""
        colors = {
            'prohibited': 'darkred',
            'casa_approval': 'red',
            'atc_clearance': 'orange',
            'notification': 'blue',
            'restricted': 'orange',
            'unrestricted': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.authorization_level, 'black'),
            obj.get_authorization_level_display()
        )
    authorization_level_display.short_description = 'Authorization Level'


@admin.register(OperationalArea)
class OperationalAreaAdmin(admin.ModelAdmin):
    """
    Admin interface for Operational Area Management
    """
    list_display = [
        'area_id',
        'name',
        'area_type',
        'airspace_class',
        'status_display',
        'rpa_permitted_display',
        'active_status',
        'controlling_authority'
    ]
    list_filter = [
        'area_type',
        'airspace_class',
        'status',
        'rpa_operations_permitted',
        'authorization_required'
    ]
    search_fields = [
        'area_id',
        'name',
        'controlling_authority',
        'casa_reference'
    ]
    fieldsets = (
        ('Area Identification', {
            'fields': (
                'area_id',
                'name',
                'area_type',
                'airspace_class'
            )
        }),
        ('Geographic Information', {
            'fields': (
                'center_latitude',
                'center_longitude',
                'radius_nautical_miles',
                'boundary_geojson'
            )
        }),
        ('Altitude Limits', {
            'fields': (
                'floor_altitude_amsl',
                'ceiling_altitude_amsl',
                'floor_height_agl',
                'ceiling_height_agl'
            )
        }),
        ('Operational Parameters', {
            'fields': (
                'status',
                'rpa_operations_permitted',
                'authorization_required'
            )
        }),
        ('Time Restrictions', {
            'fields': (
                'effective_from',
                'effective_until'
            )
        }),
        ('Contact Information', {
            'fields': (
                'controlling_authority',
                'contact_frequency',
                'contact_phone'
            )
        }),
        ('Documentation', {
            'fields': (
                'description',
                'operational_notes',
                'casa_reference'
            )
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'temporary': 'orange',
            'permanent': 'blue'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def rpa_permitted_display(self, obj):
        """Display RPA permission status"""
        if obj.rpa_operations_permitted:
            if obj.authorization_required:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠ Auth Required</span>'
                )
            else:
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Permitted</span>'
                )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Prohibited</span>'
            )
    rpa_permitted_display.short_description = 'RPA Operations'

    def active_status(self, obj):
        """Display current active status based on time restrictions"""
        if obj.is_currently_active:
            return format_html('<span style="color: green;">✓ Currently Active</span>')
        elif obj.status == 'inactive':
            return format_html('<span style="color: gray;">Inactive</span>')
        elif obj.effective_from and timezone.now() < obj.effective_from:
            return format_html(
                '<span style="color: orange;">Future Active ({})</span>',
                obj.effective_from.strftime('%d/%m/%Y %H:%M')
            )
        elif obj.effective_until and timezone.now() > obj.effective_until:
            return format_html(
                '<span style="color: red;">Expired ({})</span>',
                obj.effective_until.strftime('%d/%m/%Y %H:%M')
            )
        else:
            return format_html('<span style="color: gray;">Unknown</span>')
    active_status.short_description = 'Current Status'

    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return super().get_queryset(request).select_related('airspace_class')
