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
            "certification_required",
            "maximum_takeoff_weight",
            "maximum_operating_height",
            "maximum_speed",
            "endurance_hours",
            "payload_capacity",
            "typical_cruise_speed",
            "casa_type_certificate",
            "casa_approval_reference",
            "excluded_category_compliant",
            "flight_manual_required",
            "maintenance_manual_required",
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
            "category": forms.Select(attrs={"class": "form-select"}),
            "operation_type": forms.Select(attrs={"class": "form-select"}),
            "certification_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "maximum_takeoff_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "kg"}
            ),
            "maximum_operating_height": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "feet AGL"}
            ),
            "maximum_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "knots"}
            ),
            "endurance_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "placeholder": "hours"}
            ),
            "payload_capacity": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}
            ),
            "typical_cruise_speed": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "knots"}
            ),
            "casa_type_certificate": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA certificate number",
                }
            ),
            "casa_approval_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA approval reference",
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
            "operational_limitations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe operational limitations and restrictions",
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

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Aircraft type name is required")
        if len(name) < 2:
            raise ValidationError("Aircraft type name must be at least 2 characters")
        return name

    def clean_manufacturer(self):
        manufacturer = self.cleaned_data.get("manufacturer", "").strip()
        if not manufacturer:
            raise ValidationError("Manufacturer is required")
        return manufacturer

    def clean_model(self):
        model = self.cleaned_data.get("model", "").strip()
        if not model:
            raise ValidationError("Model is required")
        return model

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        category = cleaned_data.get("category")
        weight = cleaned_data.get("maximum_takeoff_weight")
        operation_type = cleaned_data.get("operation_type")
        certification_required = cleaned_data.get("certification_required")
        casa_cert = cleaned_data.get("casa_type_certificate")

        # Validate weight categories according to CASA regulations
        if category == "micro" and weight and weight > 0.25:
            raise ValidationError("Micro RPA must be ≤250g (0.25kg)")

        if category == "small" and weight and (weight <= 0.25 or weight > 25):
            raise ValidationError("Small RPA must be >250g and ≤25kg")

        if category == "medium" and weight and (weight <= 25 or weight > 150):
            raise ValidationError("Medium RPA must be >25kg and ≤150kg")

        if category == "large" and weight and weight <= 150:
            raise ValidationError("Large RPA must be >150kg")

        # Commercial operations validation
        if operation_type == "commercial" and certification_required and not casa_cert:
            raise ValidationError(
                "Commercial aircraft requiring certification must have CASA type certificate"
            )

        return cleaned_data


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
            # "current_flight_hours",  # AUTO-CALCULATED - removed from form for data integrity
            "maximum_flight_hours",
            "flight_manual_reference",
            "registration_date",
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
            # current_flight_hours widget removed - auto-calculated for data integrity
            "maximum_flight_hours": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "maximum hours"}
            ),
            "flight_manual_reference": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Manual reference"}
            ),
            "registration_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
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

    # clean_current_flight_hours removed - auto-calculated field ensures data integrity

    def clean_year_manufactured(self):
        year = self.cleaned_data.get("year_manufactured")
        if year:
            from datetime import datetime

            current_year = datetime.now().year
            if year < 1980:
                raise ValidationError("Aircraft year must be 1980 or later")
            if year > current_year + 2:
                raise ValidationError(
                    f"Aircraft year cannot be more than 2 years in the future"
                )
        return year

    def clean_maximum_flight_hours(self):
        max_hours = self.cleaned_data.get("maximum_flight_hours")
        if max_hours is not None and max_hours < 0:
            raise ValidationError("Maximum flight hours cannot be negative")
        return max_hours

    def clean(self):
        """Cross-field validation for data integrity"""
        cleaned_data = super().clean()

        # Date validation for maintenance and certificates
        airworthiness_date = cleaned_data.get("airworthiness_valid_until")
        insurance_date = cleaned_data.get("insurance_valid_until")
        last_maintenance = cleaned_data.get("last_maintenance_check")
        next_maintenance = cleaned_data.get("next_maintenance_due")
        registration_date = cleaned_data.get("registration_date")

        # Ensure future dates are reasonable
        from datetime import datetime, timedelta

        future_limit = datetime.now().date() + timedelta(days=3650)  # 10 years

        if airworthiness_date and airworthiness_date > future_limit:
            raise ValidationError(
                "Airworthiness date cannot be more than 10 years in the future"
            )

        if insurance_date and insurance_date > future_limit:
            raise ValidationError(
                "Insurance date cannot be more than 10 years in the future"
            )

        # Maintenance date logic
        if last_maintenance and next_maintenance:
            if next_maintenance <= last_maintenance:
                raise ValidationError(
                    "Next maintenance due must be after last maintenance check"
                )

        # Registration date validation
        if registration_date and registration_date > datetime.now().date():
            if (registration_date - datetime.now().date()).days > 30:
                raise ValidationError(
                    "Registration date cannot be more than 30 days in the future"
                )

        return cleaned_data
