from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class AircraftType(models.Model):
    """
    CASA Part 101 Aircraft Type Classifications
    Defines aircraft categories and operational limitations
    """

    CATEGORY_CHOICES = [
        ("excluded", "Excluded Category (Part 101.073)"),
        ("micro", "Micro RPA (≤250g)"),
        ("small", "Small RPA (>250g ≤25kg)"),
        ("medium", "Medium RPA (>25kg ≤150kg)"),
        ("large", "Large RPA (>150kg)"),
    ]

    OPERATION_TYPE_CHOICES = [
        ("recreational", "Recreational"),
        ("commercial", "Commercial"),
        ("research", "Research & Development"),
        ("emergency", "Emergency Services"),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Aircraft Type Name",
        help_text="Manufacturer and model designation",
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Manufacturer",
        help_text="Aircraft manufacturer name",
    )
    model = models.CharField(
        max_length=100, verbose_name="Model", help_text="Aircraft model designation"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="CASA Category",
        help_text="Part 101 operational category",
    )
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name="Operation Type",
        help_text="Authorized operation type",
    )

    # Technical Specifications
    maximum_takeoff_weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        verbose_name="MTOW (kg)",
        help_text="Maximum Takeoff Weight in kilograms",
    )
    maximum_operating_height = models.PositiveIntegerField(
        verbose_name="Maximum Operating Height (ft AGL)",
        help_text="Maximum operating height above ground level",
    )
    maximum_speed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Speed (knots)",
        help_text="Maximum operating speed in knots",
    )
    endurance_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Endurance (hours)",
        help_text="Maximum flight endurance in hours",
    )
    payload_capacity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Payload Capacity (kg)",
        help_text="Maximum payload capacity in kilograms",
    )
    typical_cruise_speed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Typical Cruise Speed (knots)",
        help_text="Typical cruise speed in knots",
    )

    # CASA Compliance Fields
    casa_type_certificate = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CASA Type Certificate",
        help_text="CASA type certificate number if applicable",
    )
    casa_approval_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Approval Reference",
        help_text="CASA approval or exemption reference",
    )
    certification_required = models.BooleanField(
        default=True,
        verbose_name="Certification Required",
        help_text="Aircraft requires CASA certification",
    )
    excluded_category_compliant = models.BooleanField(
        default=False,
        verbose_name="Excluded Category Compliant",
        help_text="Meets Part 101.073 excluded category requirements",
    )

    # Documentation
    flight_manual_required = models.BooleanField(
        default=True,
        verbose_name="Flight Manual Required",
        help_text="Aircraft requires approved flight manual",
    )
    maintenance_manual_required = models.BooleanField(
        default=True,
        verbose_name="Maintenance Manual Required",
        help_text="Aircraft requires maintenance manual",
    )

    # Requirements and Limitations
    operational_limitations = models.TextField(
        blank=True,
        verbose_name="Operational Limitations",
        help_text="Operational limitations and restrictions",
    )
    maintenance_requirements = models.TextField(
        blank=True,
        verbose_name="Maintenance Requirements",
        help_text="Maintenance requirements and schedules",
    )
    training_requirements = models.TextField(
        blank=True,
        verbose_name="Training Requirements",
        help_text="Training requirements for operators",
    )
    insurance_requirements = models.TextField(
        blank=True,
        verbose_name="Insurance Requirements",
        help_text="Insurance coverage requirements",
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Aircraft type is active and available for selection",
    )
    # Updated model with additional fields for enhanced aircraft type management

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aircraft Type"
        verbose_name_plural = "Aircraft Types"
        ordering = ["manufacturer", "model"]

    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.get_category_display()})"

    def clean(self):
        """Validate CASA compliance requirements"""
        # Validate excluded category requirements (Part 101.073)
        if self.category == "excluded":
            if self.maximum_takeoff_weight > 25:
                raise ValidationError("Excluded category aircraft must be ≤25kg MTOW")
            if self.maximum_operating_height > 400:
                raise ValidationError("Excluded category limited to 400ft AGL")
            self.excluded_category_compliant = True

        # Validate micro RPA requirements
        if self.category == "micro":
            if self.maximum_takeoff_weight > 0.25:
                raise ValidationError("Micro RPA must be ≤250g")

        # Commercial operations require type certificate for larger aircraft
        if self.operation_type == "commercial" and self.category in ["medium", "large"]:
            if not self.casa_type_certificate:
                raise ValidationError(
                    "Commercial medium/large RPA require CASA type certificate"
                )


class Aircraft(models.Model):
    """
    Individual Aircraft Registration and Configuration
    CASA Part 101 compliant aircraft records
    """

    STATUS_CHOICES = [
        ("registered", "Registered"),
        ("pending", "Registration Pending"),
        ("suspended", "Suspended"),
        ("deregistered", "Deregistered"),
    ]

    # Registration Details
    registration_mark = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Registration Mark",
        help_text="Aircraft registration identifier",
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-]{3,20}$",
                message="Registration mark must be 3-20 alphanumeric characters",
            )
        ],
    )
    aircraft_type = models.ForeignKey(
        AircraftType,
        on_delete=models.PROTECT,
        verbose_name="Aircraft Type",
        help_text="CASA approved aircraft type",
    )

    # Owner Information (linked to accounts app)
    # TODO: Design Decision - Update to accounts.StaffProfile or create CompanyProfile
    owner = models.ForeignKey(
        "accounts.ClientProfile",
        on_delete=models.PROTECT,
        verbose_name="Aircraft Owner",
        help_text="Registered owner from client profiles",
    )
    # TODO: Design Decision - Update to accounts.PilotProfile for operators
    operator = models.ForeignKey(
        "accounts.ClientProfile",
        on_delete=models.PROTECT,
        related_name="operated_aircraft",
        verbose_name="Aircraft Operator",
        help_text="Current operator (may differ from owner)",
        null=True,
        blank=True,
    )

    # Aircraft Details
    serial_number = models.CharField(
        max_length=50,
        verbose_name="Serial Number",
        help_text="Manufacturer's serial number",
    )
    year_manufactured = models.PositiveIntegerField(
        verbose_name="Year Manufactured", help_text="Year aircraft was manufactured"
    )

    # Operational Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Registration Status",
        help_text="Current CASA registration status",
    )
    airworthiness_valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Airworthiness Valid Until",
        help_text="Certificate of airworthiness expiry date",
    )

    # Insurance and Compliance
    insurance_valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Insurance Valid Until",
        help_text="Insurance coverage expiry date",
    )
    last_maintenance_check = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Maintenance Check",
        help_text="Date of last maintenance inspection",
    )
    next_maintenance_due = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next Maintenance Due",
        help_text="Date next maintenance is due",
    )

    # Operational Limitations
    current_flight_hours = models.DecimalField(  # AUTO-CALCULATED from flight logs - READ ONLY
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Current Flight Hours",
        help_text="Total accumulated flight hours (auto-calculated from flight logs)",
        editable=False,  # Prevents manual editing - data integrity protection
    )
    maximum_flight_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Flight Hours",
        help_text="Maximum approved flight hours before overhaul",
    )

    # Documentation
    flight_manual_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Flight Manual Reference",
        help_text="Flight manual document reference",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Additional aircraft notes and observations",
    )

    # Metadata
    registration_date = models.DateField(
        default=timezone.now,
        verbose_name="Registration Date",
        help_text="Date aircraft was registered",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aircraft"
        verbose_name_plural = "Aircraft"
        ordering = ["registration_mark"]

    def __str__(self):
        return f"{self.registration_mark} - {self.aircraft_type.manufacturer} {self.aircraft_type.model}"

    def clean(self):
        """Validate aircraft compliance and operational requirements"""
        # Ensure operator is specified for commercial operations
        if self.aircraft_type.operation_type == "commercial" and not self.operator:
            raise ValidationError("Commercial aircraft must have designated operator")

        # Validate airworthiness for non-excluded category
        if (
            self.aircraft_type.category != "excluded"
            and not self.airworthiness_valid_until
        ):
            raise ValidationError(
                "Non-excluded category aircraft require airworthiness certificate"
            )

        # Check maintenance due dates
        if (
            self.next_maintenance_due
            and self.next_maintenance_due < timezone.now().date()
        ):
            raise ValidationError("Aircraft maintenance is overdue")

    @property
    def is_airworthy(self):
        """Check if aircraft airworthiness is current"""
        if not self.airworthiness_valid_until:
            return self.aircraft_type.category == "excluded"
        return self.airworthiness_valid_until >= timezone.now().date()

    @property
    def is_insured(self):
        """Check if aircraft insurance is current"""
        if not self.insurance_valid_until:
            return False
        return self.insurance_valid_until >= timezone.now().date()

    @property
    def maintenance_status(self):
        """Get maintenance status"""
        if not self.next_maintenance_due:
            return "unknown"

        days_until_due = (self.next_maintenance_due - timezone.now().date()).days

        if days_until_due < 0:
            return "overdue"
        elif days_until_due <= 7:
            return "due_soon"
        else:
            return "current"

    @property
    def is_operational(self):
        """Check if aircraft is operational (airworthy, insured, maintenance current)"""
        return (
            self.status == "registered"
            and self.is_airworthy
            and self.is_insured
            and self.maintenance_status in ["current", "due_soon"]
        )

    def calculate_total_flight_hours(self):
        """
        Auto-calculate total flight hours from flight logs
        Data integrity: Single source of truth from actual flight records
        """
        from flight_operations.models import FlightLog

        total_hours = (
            FlightLog.objects.filter(aircraft=self).aggregate(
                total=models.Sum('flight_time')
            )['total']
            or 0
        )

        return total_hours

    def update_flight_hours(self):
        """
        Update current flight hours from flight logs
        Called automatically when flight logs are created/updated
        Ensures data integrity and compliance tracking
        """
        self.current_flight_hours = self.calculate_total_flight_hours()
        self.save(update_fields=['current_flight_hours'])

    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate flight hours
        Data integrity: Always ensure hours are accurate
        """
        # Auto-calculate flight hours on save (except during initial creation)
        if self.pk:  # Only for existing aircraft
            self.current_flight_hours = self.calculate_total_flight_hours()

        super().save(*args, **kwargs)
