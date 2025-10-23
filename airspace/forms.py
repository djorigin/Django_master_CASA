from django import forms
from django.core.exceptions import ValidationError

from .models import AirspaceClass, OperationalArea


class AirspaceClassForm(forms.ModelForm):
    """Form for creating and editing airspace classes"""

    class Meta:
        model = AirspaceClass
        fields = [
            "airspace_class",
            "name",
            "description",
            "authorization_level",
            "maximum_height_agl",
            "excluded_category_allowed",
            "pilot_license_required",
            "casa_regulation_reference",
        ]

        widgets = {
            "airspace_class": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter airspace class name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter detailed description of airspace class characteristics",
                }
            ),
            "authorization_level": forms.Select(attrs={"class": "form-select"}),
            "maximum_height_agl": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Maximum height in feet AGL",
                }
            ),
            "excluded_category_allowed": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "pilot_license_required": forms.Select(attrs={"class": "form-select"}),
            "casa_regulation_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA regulation or order reference",
                }
            ),
        }

        labels = {
            "airspace_class": "Airspace Class",
            "name": "Class Name",
            "description": "Description",
            "authorization_level": "Authorization Level Required",
            "maximum_height_agl": "Maximum Height AGL (feet)",
            "excluded_category_allowed": "Excluded Category Operations Allowed",
            "pilot_license_required": "Minimum Pilot License Required",
            "casa_regulation_reference": "CASA Regulation Reference",
        }

        help_texts = {
            "airspace_class": "Select the CASA airspace classification",
            "name": "Descriptive name for this airspace class",
            "description": "Detailed description of airspace characteristics and requirements",
            "authorization_level": "Level of authorization required for RPA operations",
            "maximum_height_agl": "Maximum operating height above ground level (leave blank if no limit)",
            "excluded_category_allowed": "Check if excluded category RPA operations are permitted",
            "pilot_license_required": "Minimum pilot qualification required for operations",
            "casa_regulation_reference": "Reference to relevant CASA regulation or order",
        }

    def clean_maximum_height_agl(self):
        """Validate maximum height"""
        height = self.cleaned_data.get("maximum_height_agl")
        if height is not None and height <= 0:
            raise ValidationError("Maximum height must be a positive number.")
        if height is not None and height > 60000:
            raise ValidationError(
                "Maximum height seems unreasonably high (>60,000 ft)."
            )
        return height


class OperationalAreaForm(forms.ModelForm):
    """Form for creating and editing operational areas"""

    class Meta:
        model = OperationalArea
        fields = [
            "area_id",
            "name",
            "area_type",
            "airspace_class",
            "center_latitude",
            "center_longitude",
            "radius_nautical_miles",
            "floor_altitude_amsl",
            "ceiling_altitude_amsl",
            "floor_height_agl",
            "ceiling_height_agl",
            "status",
            "rpa_operations_permitted",
            "authorization_required",
            "effective_from",
            "effective_until",
            "controlling_authority",
            "contact_frequency",
            "contact_phone",
            "description",
            "operational_notes",
            "casa_reference",
        ]

        widgets = {
            "area_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "OA-XXXXXX (6-12 alphanumeric)",
                    "pattern": "^OA-[A-Z0-9]{6,12}$",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter operational area name",
                }
            ),
            "area_type": forms.Select(attrs={"class": "form-select"}),
            "airspace_class": forms.Select(attrs={"class": "form-select"}),
            "center_latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0000001",
                    "placeholder": "-90.0 to 90.0",
                }
            ),
            "center_longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0000001",
                    "placeholder": "-180.0 to 180.0",
                }
            ),
            "radius_nautical_miles": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                    "placeholder": "Radius in nautical miles",
                }
            ),
            "floor_altitude_amsl": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Floor altitude AMSL (feet)",
                }
            ),
            "ceiling_altitude_amsl": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ceiling altitude AMSL (feet)",
                }
            ),
            "floor_height_agl": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Floor height AGL (feet)",
                }
            ),
            "ceiling_height_agl": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ceiling height AGL (feet)",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "rpa_operations_permitted": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "authorization_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "effective_from": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "effective_until": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "controlling_authority": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Authority responsible for this airspace",
                }
            ),
            "contact_frequency": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Radio frequency (e.g., 118.100)",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone number for coordination",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of area and operational considerations",
                }
            ),
            "operational_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Special operational notes and considerations",
                }
            ),
            "casa_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA NOTAM, AIP or other reference",
                }
            ),
        }

        labels = {
            "area_id": "Area ID",
            "name": "Area Name",
            "area_type": "Area Type",
            "airspace_class": "Airspace Class",
            "center_latitude": "Center Latitude (decimal degrees)",
            "center_longitude": "Center Longitude (decimal degrees)",
            "radius_nautical_miles": "Radius (Nautical Miles)",
            "floor_altitude_amsl": "Floor Altitude AMSL (feet)",
            "ceiling_altitude_amsl": "Ceiling Altitude AMSL (feet)",
            "floor_height_agl": "Floor Height AGL (feet)",
            "ceiling_height_agl": "Ceiling Height AGL (feet)",
            "status": "Status",
            "rpa_operations_permitted": "RPA Operations Permitted",
            "authorization_required": "Authorization Required",
            "effective_from": "Effective From",
            "effective_until": "Effective Until",
            "controlling_authority": "Controlling Authority",
            "contact_frequency": "Contact Frequency",
            "contact_phone": "Contact Phone",
            "description": "Description",
            "operational_notes": "Operational Notes",
            "casa_reference": "CASA Reference",
        }

        help_texts = {
            "area_id": "Unique identifier in format OA-XXXXXX (6-12 alphanumeric characters)",
            "name": "Descriptive name for the operational area",
            "area_type": "Type of operational area",
            "airspace_class": "Airspace classification for this area",
            "center_latitude": "Center point latitude in decimal degrees (-90 to 90)",
            "center_longitude": "Center point longitude in decimal degrees (-180 to 180)",
            "radius_nautical_miles": "Area radius in nautical miles (for circular areas)",
            "floor_altitude_amsl": "Area floor altitude above mean sea level",
            "ceiling_altitude_amsl": "Area ceiling altitude above mean sea level",
            "floor_height_agl": "Area floor height above ground level",
            "ceiling_height_agl": "Area ceiling height above ground level",
            "status": "Current operational status of the area",
            "rpa_operations_permitted": "Check if RPA operations are permitted in this area",
            "authorization_required": "Check if special authorization is required for operations",
            "effective_from": "Date and time when area restrictions become effective",
            "effective_until": "Date and time when area restrictions expire",
            "controlling_authority": "Authority or organization responsible for this airspace",
            "contact_frequency": "Radio frequency for area coordination",
            "contact_phone": "Phone number for area coordination",
            "description": "Detailed description of area and operational considerations",
            "operational_notes": "Special operational notes and considerations",
            "casa_reference": "Reference to CASA NOTAM, AIP or other documentation",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make airspace_class queryset more efficient
        self.fields["airspace_class"].queryset = AirspaceClass.objects.all().order_by(
            "airspace_class"
        )

    def clean_area_id(self):
        """Validate area ID format and uniqueness"""
        area_id = self.cleaned_data.get("area_id", "").strip().upper()

        if not area_id:
            raise ValidationError("Area ID is required.")

        # Validate format
        import re

        if not re.match(r"^OA-[A-Z0-9]{6,12}$", area_id):
            raise ValidationError(
                "Area ID must be in format OA-XXXXXX (6-12 alphanumeric characters)."
            )

        # Check uniqueness (exclude current instance if updating)
        queryset = OperationalArea.objects.filter(area_id=area_id)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("This Area ID is already in use.")

        return area_id

    def clean_center_latitude(self):
        """Validate latitude"""
        latitude = self.cleaned_data.get("center_latitude")
        if latitude is not None and not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees.")
        return latitude

    def clean_center_longitude(self):
        """Validate longitude"""
        longitude = self.cleaned_data.get("center_longitude")
        if longitude is not None and not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees.")
        return longitude

    def clean_radius_nautical_miles(self):
        """Validate radius"""
        radius = self.cleaned_data.get("radius_nautical_miles")
        if radius is not None and radius <= 0:
            raise ValidationError("Radius must be a positive number.")
        if radius is not None and radius > 1000:
            raise ValidationError("Radius seems unreasonably large (>1000 NM).")
        return radius

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        # Validate altitude parameters
        floor_amsl = cleaned_data.get("floor_altitude_amsl")
        ceiling_amsl = cleaned_data.get("ceiling_altitude_amsl")
        floor_agl = cleaned_data.get("floor_height_agl")
        ceiling_agl = cleaned_data.get("ceiling_height_agl")

        if floor_amsl and ceiling_amsl and floor_amsl >= ceiling_amsl:
            raise ValidationError("Floor altitude must be below ceiling altitude.")

        if floor_agl and ceiling_agl and floor_agl >= ceiling_agl:
            raise ValidationError("Floor height must be below ceiling height.")

        # Validate time restrictions
        effective_from = cleaned_data.get("effective_from")
        effective_until = cleaned_data.get("effective_until")

        if effective_from and effective_until and effective_from >= effective_until:
            raise ValidationError(
                "Effective from date must be before effective until date."
            )

        return cleaned_data
