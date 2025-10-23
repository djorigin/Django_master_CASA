from django import forms
from django.core.exceptions import ValidationError

from .models import Aircraft, AircraftType


class AircraftTypeForm(forms.ModelForm):
    """Form for creating and editing aircraft types"""

    class Meta:
        model = AircraftType
        fields = [
            "name",
            "manufacturer",
            "model",
            "category",
            "operation_type",
            "max_takeoff_weight",
            "max_operating_altitude",
            "max_operating_speed",
            "endurance_hours",
            "payload_capacity",
            "typical_cruise_speed",
            "certification_required",
            "casa_approval_reference",
            "operational_limitations",
            "maintenance_requirements",
            "training_requirements",
            "insurance_requirements",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter aircraft type name",
                }
            ),
            "manufacturer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter manufacturer name",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter model designation",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "operation_type": forms.Select(attrs={"class": "form-control"}),
            "max_takeoff_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}
            ),
            "max_operating_altitude": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "feet AGL"}
            ),
            "max_operating_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "km/h"}
            ),
            "endurance_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "placeholder": "hours"}
            ),
            "payload_capacity": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}
            ),
            "typical_cruise_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "km/h"}
            ),
            "certification_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "casa_approval_reference": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CASA reference number"}
            ),
            "operational_limitations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe operational limitations",
                }
            ),
            "maintenance_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe maintenance requirements",
                }
            ),
            "training_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe training requirements",
                }
            ),
            "insurance_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe insurance requirements",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_max_takeoff_weight(self):
        weight = self.cleaned_data.get("max_takeoff_weight")
        if weight is not None and weight <= 0:
            raise ValidationError("Weight must be greater than 0")
        return weight

    def clean_max_operating_altitude(self):
        altitude = self.cleaned_data.get("max_operating_altitude")
        if altitude is not None and altitude < 0:
            raise ValidationError("Altitude cannot be negative")
        return altitude


class AircraftForm(forms.ModelForm):
    """Form for creating and editing aircraft"""

    class Meta:
        model = Aircraft
        fields = [
            "aircraft_id",
            "aircraft_type",
            "serial_number",
            "registration_number",
            "status",
            "owner",
            "operator",
            "manufacture_date",
            "acquisition_date",
            "location",
            "flight_hours",
            "cycle_count",
            "last_inspection_date",
            "next_inspection_due",
            "airworthiness_certificate",
            "certificate_expiry_date",
            "insurance_policy_number",
            "insurance_expiry_date",
            "operating_limitations",
            "maintenance_notes",
            "is_active",
        ]

        widgets = {
            "aircraft_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter aircraft ID"}
            ),
            "aircraft_type": forms.Select(attrs={"class": "form-control"}),
            "serial_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter serial number"}
            ),
            "registration_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter registration"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "owner": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter owner name"}
            ),
            "operator": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter operator name"}
            ),
            "manufacture_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "acquisition_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Current location"}
            ),
            "flight_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "placeholder": "hours"}
            ),
            "cycle_count": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "flight cycles"}
            ),
            "last_inspection_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "next_inspection_due": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "airworthiness_certificate": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Certificate number"}
            ),
            "certificate_expiry_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "insurance_policy_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Policy number"}
            ),
            "insurance_expiry_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "operating_limitations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe any operating limitations",
                }
            ),
            "maintenance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional maintenance notes",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_aircraft_id(self):
        aircraft_id = self.cleaned_data.get("aircraft_id")
        if aircraft_id:
            # Check for duplicate aircraft IDs (excluding current instance)
            existing = Aircraft.objects.filter(aircraft_id=aircraft_id)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Aircraft ID must be unique")
        return aircraft_id

    def clean_registration_number(self):
        registration = self.cleaned_data.get("registration_number")
        if registration:
            # Check for duplicate registration numbers (excluding current instance)
            existing = Aircraft.objects.filter(registration_number=registration)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Registration number must be unique")
        return registration
