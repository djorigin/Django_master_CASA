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
            "maximum_takeoff_weight",
            "maximum_operating_height",
            "maximum_speed",
            "casa_type_certificate",
            "excluded_category_compliant",
            "flight_manual_required",
            "maintenance_manual_required",
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
            "maximum_takeoff_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "kg"}
            ),
            "maximum_operating_height": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "feet AGL"}
            ),
            "maximum_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "knots"}
            ),
            "casa_type_certificate": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA type certificate number",
                }
            ),
            "excluded_category_compliant": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "flight_manual_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "maintenance_manual_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_maximum_takeoff_weight(self):
        weight = self.cleaned_data.get("maximum_takeoff_weight")
        if weight is not None and weight <= 0:
            raise ValidationError("Weight must be greater than 0")
        return weight

    def clean_maximum_operating_height(self):
        height = self.cleaned_data.get("maximum_operating_height")
        if height is not None and height < 0:
            raise ValidationError("Height cannot be negative")
        return height


class AircraftForm(forms.ModelForm):
    """Form for creating and editing aircraft"""

    class Meta:
        model = Aircraft
        fields = [
            "aircraft_id",
            "aircraft_type",
            "serial_number",
            "registration_mark",
            "status",
            "current_location",
            "owner_operator",
            "manufacture_date",
            "acquisition_date",
            "flight_hours",
            "flight_cycles",
            "last_inspection_date",
            "next_inspection_due_date",
            "current_airworthiness_status",
            "maintenance_notes",
        ]

        widgets = {
            "aircraft_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter aircraft ID"}
            ),
            "aircraft_type": forms.Select(attrs={"class": "form-control"}),
            "serial_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter serial number"}
            ),
            "registration_mark": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter registration mark",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "current_location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Current location"}
            ),
            "owner_operator": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Owner/Operator name"}
            ),
            "manufacture_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "acquisition_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "flight_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "placeholder": "hours"}
            ),
            "flight_cycles": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "flight cycles"}
            ),
            "last_inspection_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "next_inspection_due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "current_airworthiness_status": forms.Select(
                attrs={"class": "form-control"}
            ),
            "maintenance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional maintenance notes",
                }
            ),
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
