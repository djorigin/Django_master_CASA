from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateTimeInput

from .models import IncidentReport, IncidentType


class IncidentTypeForm(forms.ModelForm):
    """Form for creating and updating Incident Types"""

    class Meta:
        model = IncidentType
        fields = [
            'name',
            'category',
            'severity',
            'casa_reportable',
            'reporting_timeframe_hours',
            'immediate_notification_required',
            'investigation_required',
            'grounding_required',
            'description',
            'casa_reference',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter incident type name',
                }
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'casa_reportable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reporting_timeframe_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1', 'max': '168'}  # Max 7 days
            ),
            'immediate_notification_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'investigation_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'grounding_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Detailed description of incident type and criteria',
                }
            ),
            'casa_reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'CASA regulation or advisory material reference',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required based on CASA compliance
        if self.instance and self.instance.casa_reportable:
            self.fields['reporting_timeframe_hours'].required = True

    def clean(self):
        cleaned_data = super().clean()
        casa_reportable = cleaned_data.get('casa_reportable')
        reporting_timeframe = cleaned_data.get('reporting_timeframe_hours')
        immediate_notification = cleaned_data.get('immediate_notification_required')

        # Validation for CASA reportable incidents
        if casa_reportable and not reporting_timeframe:
            raise ValidationError(
                {
                    'reporting_timeframe_hours': 'Reporting timeframe is required for CASA reportable incidents.'
                }
            )

        # Immediate notification requires CASA reportable
        if immediate_notification and not casa_reportable:
            raise ValidationError(
                {
                    'immediate_notification_required': 'Immediate notification can only be set for CASA reportable incidents.'
                }
            )

        return cleaned_data


class IncidentReportForm(forms.ModelForm):
    """Form for creating and updating Incident Reports"""

    class Meta:
        model = IncidentReport
        fields = [
            'incident_type',
            'aircraft',
            'pilot_in_command',
            'incident_date',
            'location_description',
            'latitude',
            'longitude',
            'flight_phase',
            'flight_hours_on_aircraft',
            'weather_conditions',
            'wind_speed_knots',
            'visibility_meters',
            'summary',
            'detailed_description',
            'aircraft_damage',
            'property_damage',
            'injuries',
            'contributing_factors',
            'immediate_causes',
            'immediate_actions',
            'preventive_actions',
            'follow_up_required',
            'follow_up_actions',
        ]
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'aircraft': forms.Select(attrs={'class': 'form-select'}),
            'pilot_in_command': forms.Select(attrs={'class': 'form-select'}),
            'incident_date': DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'location_description': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Describe incident location',
                }
            ),
            'latitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.0000001',
                    'placeholder': 'Decimal degrees (-90 to 90)',
                }
            ),
            'longitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.0000001',
                    'placeholder': 'Decimal degrees (-180 to 180)',
                }
            ),
            'flight_phase': forms.Select(attrs={'class': 'form-select'}),
            'flight_hours_on_aircraft': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}
            ),
            'weather_conditions': forms.Select(attrs={'class': 'form-select'}),
            'wind_speed_knots': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '200'}
            ),
            'visibility_meters': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '50000'}
            ),
            'summary': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Brief summary of what happened',
                }
            ),
            'detailed_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Detailed description of incident sequence',
                }
            ),
            'aircraft_damage': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe any aircraft damage',
                }
            ),
            'property_damage': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe any property damage',
                }
            ),
            'injuries': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe any injuries',
                }
            ),
            'contributing_factors': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Factors that contributed to the incident',
                }
            ),
            'immediate_causes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Immediate causes of the incident',
                }
            ),
            'immediate_actions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Actions taken immediately after incident',
                }
            ),
            'preventive_actions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Actions taken to prevent recurrence',
                }
            ),
            'follow_up_required': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'follow_up_actions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Required follow-up actions',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Auto-populate reported_by field if creating new report
        if not self.instance.pk and user:
            self.reported_by = user

        # Filter aircraft and pilot choices based on user's organization if needed
        # This can be enhanced with proper permissions

        # Make follow_up_actions required if follow_up_required is checked
        self.fields['follow_up_actions'].required = False

    def clean(self):
        cleaned_data = super().clean()
        follow_up_required = cleaned_data.get('follow_up_required')
        follow_up_actions = cleaned_data.get('follow_up_actions')

        # Validate follow-up requirements
        if follow_up_required and not follow_up_actions:
            raise ValidationError(
                {
                    'follow_up_actions': 'Follow-up actions must be specified when follow-up is required.'
                }
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set reported_by if it was provided during init
        if hasattr(self, 'reported_by'):
            instance.reported_by = self.reported_by

        if commit:
            instance.save()
        return instance


class IncidentInvestigationForm(forms.ModelForm):
    """Form for updating investigation details"""

    class Meta:
        model = IncidentReport
        fields = [
            'investigation_findings',
            'investigation_completed',
            'investigation_completed_date',
        ]
        widgets = {
            'investigation_findings': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': 'Summary of investigation findings',
                }
            ),
            'investigation_completed': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'investigation_completed_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        investigation_completed = cleaned_data.get('investigation_completed')
        investigation_completed_date = cleaned_data.get('investigation_completed_date')
        investigation_findings = cleaned_data.get('investigation_findings')

        # Validation for completed investigations
        if investigation_completed and not investigation_completed_date:
            raise ValidationError(
                {
                    'investigation_completed_date': 'Completion date is required when investigation is marked as completed.'
                }
            )

        if investigation_completed and not investigation_findings:
            raise ValidationError(
                {
                    'investigation_findings': 'Investigation findings are required when investigation is completed.'
                }
            )

        return cleaned_data


class CASAReportingForm(forms.ModelForm):
    """Form for CASA reporting details"""

    class Meta:
        model = IncidentReport
        fields = [
            'casa_reported',
            'casa_report_date',
            'casa_reference_number',
        ]
        widgets = {
            'casa_reported': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'casa_report_date': DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'casa_reference_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'CASA incident reference number',
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        casa_reported = cleaned_data.get('casa_reported')
        casa_report_date = cleaned_data.get('casa_report_date')
        casa_reference_number = cleaned_data.get('casa_reference_number')

        # Validation for CASA reporting
        if casa_reported and not casa_report_date:
            raise ValidationError(
                {
                    'casa_report_date': 'Report date is required when incident is marked as reported to CASA.'
                }
            )

        if casa_reported and not casa_reference_number:
            raise ValidationError(
                {
                    'casa_reference_number': 'CASA reference number is required when incident is reported.'
                }
            )

        return cleaned_data
