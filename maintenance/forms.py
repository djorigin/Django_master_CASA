from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput, DateTimeInput
from django.utils import timezone

from .models import (
    MaintenanceRecord,
    MaintenanceType,
    RPASMaintenanceEntry,
    RPASTechnicalLogPartA,
    RPASTechnicalLogPartB,
)


class MaintenanceTypeForm(forms.ModelForm):
    """Form for creating and updating Maintenance Types"""

    class Meta:
        model = MaintenanceType
        fields = [
            'name',
            'type_category',
            'priority',
            'description',
            'reference_manual',
            'frequency_hours',
            'frequency_days',
            'frequency_cycles',
            'casa_required',
            'licensed_engineer_required',
            'casa_form_required',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter maintenance type name',
                }
            ),
            'type_category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Detailed description of maintenance procedure',
                }
            ),
            'reference_manual': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Aircraft maintenance manual reference',
                }
            ),
            'frequency_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}
            ),
            'frequency_days': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),
            'frequency_cycles': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),
            'casa_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'licensed_engineer_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'casa_form_required': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Required CASA form (e.g., Form 337)',
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        type_category = cleaned_data.get('type_category')
        frequency_hours = cleaned_data.get('frequency_hours')
        frequency_days = cleaned_data.get('frequency_days')
        frequency_cycles = cleaned_data.get('frequency_cycles')

        # Validate frequency parameters for scheduled maintenance
        if type_category not in ['repair', 'modification']:
            if not any([frequency_hours, frequency_days, frequency_cycles]):
                raise ValidationError(
                    'At least one frequency parameter (hours, days, or cycles) must be specified for scheduled maintenance.'
                )

        return cleaned_data


class MaintenanceRecordForm(forms.ModelForm):
    """Form for creating and updating Maintenance Records"""

    class Meta:
        model = MaintenanceRecord
        fields = [
            'aircraft',
            'maintenance_type',
            'performed_by',
            'supervised_by',
            'scheduled_date',
            'pre_maintenance_hours',
            'work_performed',
            'defects_found',
            'corrective_actions',
            'parts_used',
            'labor_hours',
            'parts_cost',
        ]
        widgets = {
            'aircraft': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'performed_by': forms.Select(attrs={'class': 'form-select'}),
            'supervised_by': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'pre_maintenance_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}
            ),
            'work_performed': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Detailed description of work performed',
                }
            ),
            'defects_found': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Any defects or issues found during maintenance',
                }
            ),
            'corrective_actions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Corrective actions taken to address defects',
                }
            ),
            'parts_used': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'List of parts used during maintenance',
                }
            ),
            'labor_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1'}
            ),
            'parts_cost': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter staff profiles to only maintenance personnel if needed
        # This can be enhanced with proper role filtering

        # Auto-populate pre_maintenance_hours from aircraft if creating new record
        if not self.instance.pk and 'aircraft' in self.initial:
            try:
                from aircraft.models import Aircraft

                aircraft = Aircraft.objects.get(pk=self.initial['aircraft'])
                self.fields['pre_maintenance_hours'].initial = (
                    aircraft.current_flight_hours
                )
            except:
                pass

    def clean(self):
        cleaned_data = super().clean()
        maintenance_type = cleaned_data.get('maintenance_type')
        supervised_by = cleaned_data.get('supervised_by')

        # Validate supervision requirements
        if (
            maintenance_type
            and maintenance_type.requires_licensed_engineer
            and not supervised_by
        ):
            raise ValidationError(
                {
                    'supervised_by': 'Licensed engineer supervision is required for this maintenance type.'
                }
            )

        return cleaned_data


class MaintenanceCompletionForm(forms.ModelForm):
    """Form for completing maintenance records"""

    class Meta:
        model = MaintenanceRecord
        fields = [
            'completed_date',
            'post_maintenance_hours',
            'completion_status',
            'casa_form_completed',
            'return_to_service_authorization',
            'followup_required',
            'next_maintenance_due',
        ]
        widgets = {
            'completed_date': DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'post_maintenance_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}
            ),
            'completion_status': forms.Select(attrs={'class': 'form-select'}),
            'casa_form_completed': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'return_to_service_authorization': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Authorization for return to service',
                }
            ),
            'followup_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'next_maintenance_due': DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default completion date to now
        if not self.instance.completed_date:
            self.fields['completed_date'].initial = timezone.now()

    def clean(self):
        cleaned_data = super().clean()
        return_to_service_authorization = cleaned_data.get(
            'return_to_service_authorization'
        )
        completion_status = cleaned_data.get('completion_status')
        followup_required = cleaned_data.get('followup_required')

        # Can only authorize return to service if maintenance is satisfactory
        if return_to_service_authorization and completion_status != 'satisfactory':
            raise ValidationError(
                {
                    'return_to_service_authorization': 'Aircraft can only be returned to service if maintenance completion is satisfactory.'
                }
            )

        return cleaned_data


class RPASTechnicalLogPartAForm(forms.ModelForm):
    """Form for RPAS Technical Log Part A (Maintenance and Defects)"""

    class Meta:
        model = RPASTechnicalLogPartA
        fields = [
            'aircraft',
            'maintenance_schedule_reference',
            'part_101_moc_issued_by',
            'part_101_moc_issued_on',
            'part_101_moc_signed_by',
            'major_defects_notes',
            'minor_defects_notes',
            'current_status',
        ]
        widgets = {
            'aircraft': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_schedule_reference': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Reference to manufacturer maintenance system or Operations Manual',
                }
            ),
            'part_101_moc_issued_by': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Authority certifying MOC compliance',
                }
            ),
            'part_101_moc_issued_on': DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'part_101_moc_signed_by': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name and ARNC of certifying authority',
                }
            ),
            'major_defects_notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Major defects that preclude further flight until rectified',
                }
            ),
            'minor_defects_notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Minor defects to be checked at each Daily Inspection',
                }
            ),
            'current_status': forms.Select(attrs={'class': 'form-select'}),
        }


class RPASTechnicalLogPartBForm(forms.ModelForm):
    """Form for RPAS Technical Log Part B (Daily Inspection and Time in Service)"""

    class Meta:
        model = RPASTechnicalLogPartB
        fields = [
            'technical_log_part_a',
            'date',
            'daily_inspection_certification',
            'signature_type',
            'signature_identifier',
            'flight_time',
            'daily_notes',
            'inspection_satisfactory',
            'defects_found',
            'inspector',
        ]
        widgets = {
            'technical_log_part_a': forms.Select(attrs={'class': 'form-select'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'daily_inspection_certification': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Daily inspection certification details (IFP, MC, approved crew member, etc.)',
                }
            ),
            'signature_type': forms.Select(attrs={'class': 'form-select'}),
            'signature_identifier': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ARN number or certificate identifier',
                }
            ),
            'flight_time': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'daily_notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Additional notes for this daily inspection',
                }
            ),
            'inspection_satisfactory': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'defects_found': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Any defects found during daily inspection',
                }
            ),
            'inspector': forms.Select(attrs={'class': 'form-select'}),
        }


class RPASMaintenanceEntryForm(forms.ModelForm):
    """Form for RPAS Maintenance Entries"""

    class Meta:
        model = RPASMaintenanceEntry
        fields = [
            'technical_log_part_a',
            'maintenance_record',
            'item_description',
            'due_date_tts',
            'completed_date_arn',
            'completed_by_name',
            'completed_by_arn',
            'defect_category',
            'rpas_specific_notes',
        ]
        widgets = {
            'technical_log_part_a': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_record': forms.Select(attrs={'class': 'form-select'}),
            'item_description': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Maintenance item description for RPAS log',
                }
            ),
            'due_date_tts': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date_arn': DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'completed_by_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name of person who completed maintenance',
                }
            ),
            'completed_by_arn': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ARN of person who completed maintenance',
                }
            ),
            'defect_category': forms.Select(attrs={'class': 'form-select'}),
            'rpas_specific_notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Additional notes specific to RPAS Technical Log requirements',
                }
            ),
        }
