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
            "category": forms.Select(attrs={"class": "form-select"}),
            "operation_type": forms.Select(attrs={"class": "form-select"}),
            "maximum_takeoff_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}
            ),
            "maximum_operating_height": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "feet AGL"}
            ),
            "maximum_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "km/h"}
            ),
            "casa_type_certificate": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA certificate number",
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
            "registration_mark",
            "aircraft_type",
            "owner",
            "operator",
            "serial_number",
            "year_manufactured",
            "status",
            "airworthiness_valid_until",
            "insurance_valid_until",
            "last_maintenance_check",
            "next_maintenance_due",
            "current_flight_hours",
            "maximum_flight_hours",
            "flight_manual_reference",
            "notes",
        ]

        widgets = {
            "registration_mark": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter registration mark",
                }
            ),
            "aircraft_type": forms.Select(attrs={"class": "form-select"}),
            "owner": forms.Select(attrs={"class": "form-select"}),
            "operator": forms.Select(attrs={"class": "form-select"}),
            "serial_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter serial number"}
            ),
            "year_manufactured": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter year"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "airworthiness_valid_until": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "insurance_valid_until": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "last_maintenance_check": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "next_maintenance_due": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "current_flight_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "hours"}
            ),
            "maximum_flight_hours": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "maximum hours"}
            ),
            "flight_manual_reference": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Manual reference"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional notes",
                }
            ),
        }

    def clean_registration_mark(self):
        registration_mark = self.cleaned_data.get("registration_mark")
        if registration_mark:
            # Check for duplicate registration marks (excluding current instance)
            existing = Aircraft.objects.filter(registration_mark=registration_mark)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Registration mark must be unique")
        return registration_mark

    def clean_current_flight_hours(self):
        current_hours = self.cleaned_data.get("current_flight_hours")
        maximum_hours = self.cleaned_data.get("maximum_flight_hours")

        if current_hours is not None and current_hours < 0:
            raise ValidationError("Flight hours cannot be negative")

        if (
            current_hours is not None
            and maximum_hours is not None
            and current_hours > maximum_hours
        ):
            raise ValidationError(
                "Current flight hours cannot exceed maximum flight hours"
            )

        return current_hours
