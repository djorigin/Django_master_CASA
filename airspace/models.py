import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class AirspaceClass(models.Model):
    """
    Australian Airspace Classifications
    Based on CASA airspace structure for RPA operations
    """

    CLASS_CHOICES = [
        ("A", "Class A - Controlled Airspace"),
        ("C", "Class C - Controlled Airspace"),
        ("D", "Class D - Controlled Airspace"),
        ("E", "Class E - Controlled Airspace"),
        ("G", "Class G - Uncontrolled Airspace"),
    ]

    AUTHORIZATION_LEVEL_CHOICES = [
        ("prohibited", "Prohibited - No RPA Operations"),
        ("casa_approval", "CASA Approval Required"),
        ("atc_clearance", "ATC Clearance Required"),
        ("notification", "Notification Required"),
        ("restricted", "Restricted Operations"),
        ("unrestricted", "Unrestricted (Subject to Part 101)"),
    ]

    airspace_class = models.CharField(
        max_length=1,
        choices=CLASS_CHOICES,
        unique=True,
        verbose_name="Airspace Class",
        help_text="CASA airspace classification",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Class Name",
        help_text="Descriptive name for airspace class",
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of airspace class characteristics",
    )

    # RPA Operation Parameters
    authorization_level = models.CharField(
        max_length=20,
        choices=AUTHORIZATION_LEVEL_CHOICES,
        verbose_name="Authorization Level",
        help_text="Required authorization level for RPA operations",
    )
    maximum_height_agl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Height AGL (feet)",
        help_text="Maximum operating height above ground level",
    )
    excluded_category_allowed = models.BooleanField(
        default=False,
        verbose_name="Excluded Category Allowed",
        help_text="Excluded category RPA operations permitted",
    )

    # Operational Requirements
    pilot_license_required = models.CharField(
        max_length=20,
        choices=[
            ("none", "None Required"),
            ("reoc", "ReOC Required"),
            ("rpl", "Remote Pilot License"),
            ("cpl", "Commercial Pilot License"),
        ],
        default="none",
        verbose_name="Pilot License Required",
        help_text="Minimum pilot qualification required",
    )

    # CASA References
    casa_regulation_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Regulation Reference",
        help_text="Relevant CASA regulation or order",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Airspace Class"
        verbose_name_plural = "Airspace Classes"
        ordering = ["airspace_class"]

    def __str__(self):
        return f"Class {self.airspace_class} - {self.name}"


class OperationalArea(models.Model):
    """
    Defined Operational Areas for RPA Operations
    Geographic areas with specific operational parameters and restrictions
    """

    AREA_TYPE_CHOICES = [
        ("aerodrome", "Aerodrome/Airport"),
        ("controlled_airspace", "Controlled Airspace"),
        ("restricted_area", "Restricted Area"),
        ("danger_area", "Danger Area"),
        ("prohibited_area", "Prohibited Area"),
        ("military_area", "Military Operations Area"),
        ("national_park", "National Park"),
        ("populated_area", "Populated Area"),
        ("emergency_area", "Emergency Operations Area"),
        ("training_area", "Training Area"),
        ("commercial_area", "Commercial Operations Area"),
        ("research_area", "Research Area"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("temporary", "Temporary"),
        ("permanent", "Permanent"),
    ]

    # Area Identification
    area_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Area ID",
        help_text="Unique identifier for operational area",
        validators=[
            RegexValidator(
                regex=r"^OA-[A-Z0-9]{6,12}$",
                message="Format: OA-XXXXXX (6-12 alphanumeric characters)",
            )
        ],
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Area Name",
        help_text="Descriptive name for operational area",
    )
    area_type = models.CharField(
        max_length=20,
        choices=AREA_TYPE_CHOICES,
        verbose_name="Area Type",
        help_text="Type of operational area",
    )

    # Geographic Information
    airspace_class = models.ForeignKey(
        AirspaceClass,
        on_delete=models.PROTECT,
        verbose_name="Airspace Class",
        help_text="Airspace classification for this area",
    )
    center_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Center Latitude",
        help_text="Center latitude in decimal degrees",
    )
    center_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Center Longitude",
        help_text="Center longitude in decimal degrees",
    )
    radius_nautical_miles = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Radius (Nautical Miles)",
        help_text="Area radius in nautical miles (for circular areas)",
    )

    # Boundary Definition (GeoJSON format)
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Boundary GeoJSON",
        help_text="Precise boundary definition in GeoJSON format",
    )

    # Altitude Limits
    floor_altitude_amsl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Floor Altitude AMSL (feet)",
        help_text="Area floor altitude above mean sea level",
    )
    ceiling_altitude_amsl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Ceiling Altitude AMSL (feet)",
        help_text="Area ceiling altitude above mean sea level",
    )
    floor_height_agl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Floor Height AGL (feet)",
        help_text="Area floor height above ground level",
    )
    ceiling_height_agl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Ceiling Height AGL (feet)",
        help_text="Area ceiling height above ground level",
    )

    # Operational Parameters
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="Status",
        help_text="Current status of operational area",
    )
    rpa_operations_permitted = models.BooleanField(
        default=True,
        verbose_name="RPA Operations Permitted",
        help_text="RPA operations are permitted in this area",
    )
    authorization_required = models.BooleanField(
        default=False,
        verbose_name="Authorization Required",
        help_text="Special authorization required for operations",
    )

    # Time-based Restrictions
    effective_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Effective From",
        help_text="Date/time area restrictions become effective",
    )
    effective_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Effective Until",
        help_text="Date/time area restrictions expire",
    )

    # Contact Information
    controlling_authority = models.CharField(
        max_length=100,
        verbose_name="Controlling Authority",
        help_text="Authority responsible for this airspace area",
    )
    contact_frequency = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Contact Frequency",
        help_text="Radio frequency for area coordination",
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Contact Phone",
        help_text="Phone number for area coordination",
    )

    # Documentation
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of area and operational considerations",
    )
    operational_notes = models.TextField(
        blank=True,
        verbose_name="Operational Notes",
        help_text="Special operational notes and considerations",
    )
    casa_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Reference",
        help_text="CASA NOTAM, AIP or other reference",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Operational Area"
        verbose_name_plural = "Operational Areas"
        ordering = ["area_id"]

    def __str__(self):
        return f"{self.area_id} - {self.name}"

    def clean(self):
        """Validate operational area parameters"""
        # Validate coordinates
        if not (-90 <= self.center_latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees")

        if not (-180 <= self.center_longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees")

        # Validate altitude parameters
        if (
            self.floor_altitude_amsl
            and self.ceiling_altitude_amsl
            and self.floor_altitude_amsl >= self.ceiling_altitude_amsl
        ):
            raise ValidationError("Floor altitude must be below ceiling altitude")

        if (
            self.floor_height_agl
            and self.ceiling_height_agl
            and self.floor_height_agl >= self.ceiling_height_agl
        ):
            raise ValidationError("Floor height must be below ceiling height")

        # Validate time restrictions
        if (
            self.effective_from
            and self.effective_until
            and self.effective_from >= self.effective_until
        ):
            raise ValidationError(
                "Effective from date must be before effective until date"
            )

        # Validate GeoJSON if provided
        if self.boundary_geojson:
            try:
                # Basic GeoJSON validation
                if not isinstance(self.boundary_geojson, dict):
                    raise ValidationError(
                        "Boundary GeoJSON must be a valid JSON object"
                    )
                if "type" not in self.boundary_geojson:
                    raise ValidationError("GeoJSON must have a 'type' field")
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Invalid GeoJSON format: {e}")

    @property
    def is_currently_active(self):
        """Check if area is currently active based on time restrictions"""
        if self.status != "active":
            return False

        now = timezone.now()

        if self.effective_from and now < self.effective_from:
            return False

        if self.effective_until and now > self.effective_until:
            return False

        return True

    @property
    def altitude_range_description(self):
        """Get human-readable altitude range description"""
        parts = []

        if self.floor_altitude_amsl or self.floor_height_agl:
            floor = self.floor_altitude_amsl or f"{self.floor_height_agl} AGL"
            parts.append(f"Floor: {floor} ft")

        if self.ceiling_altitude_amsl or self.ceiling_height_agl:
            ceiling = self.ceiling_altitude_amsl or f"{self.ceiling_height_agl} AGL"
            parts.append(f"Ceiling: {ceiling} ft")

        return " | ".join(parts) if parts else "No altitude restrictions"

    def get_distance_from_point(self, latitude, longitude):
        """
        Calculate distance from a point to the center of this area
        Returns distance in nautical miles
        """
        from math import asin, cos, radians, sin, sqrt

        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(
            radians,
            [
                float(self.center_latitude),
                float(self.center_longitude),
                latitude,
                longitude,
            ],
        )

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Radius of earth in nautical miles
        r = 3440.065

        return c * r
