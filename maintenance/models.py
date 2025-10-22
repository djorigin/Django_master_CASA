from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class MaintenanceType(models.Model):
    """
    CASA Part 101 Maintenance Type Classifications
    Defines different types of maintenance activities and their requirements
    """

    TYPE_CHOICES = [
        ("daily_inspection", "Daily Inspection"),
        ("pre_flight", "Pre-Flight Check"),
        ("post_flight", "Post-Flight Check"),
        ("periodic", "Periodic Maintenance"),
        ("100_hour", "100 Hour Inspection"),
        ("annual", "Annual Inspection"),
        ("repair", "Repair Work"),
        ("modification", "Modification"),
        ("overhaul", "Overhaul"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("critical", "Critical - Grounding"),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Maintenance Type Name",
        help_text="Descriptive name for maintenance type",
    )
    type_category = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type Category",
        help_text="CASA maintenance category",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priority Level",
        help_text="Maintenance priority level",
    )

    # Scheduling Parameters
    frequency_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frequency (Flight Hours)",
        help_text="Maintenance interval in flight hours",
    )
    frequency_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frequency (Calendar Days)",
        help_text="Maintenance interval in calendar days",
    )
    frequency_cycles = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frequency (Flight Cycles)",
        help_text="Maintenance interval in flight cycles",
    )

    # CASA Compliance
    casa_required = models.BooleanField(
        default=True,
        verbose_name="CASA Required",
        help_text="Required by CASA regulations",
    )
    licensed_engineer_required = models.BooleanField(
        default=False,
        verbose_name="Licensed Engineer Required",
        help_text="Requires licensed aircraft maintenance engineer",
    )
    casa_form_required = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="CASA Form Required",
        help_text="Required CASA maintenance form (e.g., Form 337)",
    )

    # Documentation
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of maintenance procedures",
    )
    reference_manual = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Reference Manual",
        help_text="Aircraft maintenance manual reference",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Maintenance Type"
        verbose_name_plural = "Maintenance Types"
        ordering = ["priority", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_priority_display()})"

    def clean(self):
        """Validate maintenance type configuration"""
        # At least one frequency parameter must be specified
        if not any([self.frequency_hours, self.frequency_days, self.frequency_cycles]):
            if self.type_category not in ["repair", "modification"]:
                raise ValidationError(
                    "At least one frequency parameter must be specified for scheduled maintenance"
                )


class MaintenanceRecord(models.Model):
    """
    Individual Maintenance Records for Aircraft
    CASA Part 101 compliant maintenance logging
    """

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("deferred", "Deferred"),
        ("cancelled", "Cancelled"),
    ]

    COMPLETION_STATUS_CHOICES = [
        ("satisfactory", "Satisfactory"),
        ("unsatisfactory", "Unsatisfactory"),
        ("partial", "Partially Complete"),
        ("requires_followup", "Requires Follow-up"),
    ]

    # Record Identification
    maintenance_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Maintenance ID",
        help_text="Unique maintenance record identifier",
        validators=[
            RegexValidator(
                regex=r"^MNT-\d{4}-\d{6}$", message="Format: MNT-YYYY-XXXXXX"
            )
        ],
    )

    # Related Objects
    aircraft = models.ForeignKey(
        "aircraft.Aircraft",
        on_delete=models.PROTECT,
        verbose_name="Aircraft",
        help_text="Aircraft being maintained",
    )
    maintenance_type = models.ForeignKey(
        MaintenanceType,
        on_delete=models.PROTECT,
        verbose_name="Maintenance Type",
        help_text="Type of maintenance being performed",
    )

    # Personnel
    performed_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="performed_maintenance",
        verbose_name="Performed By",
        help_text="Maintenance technician who performed work",
    )
    supervised_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="supervised_maintenance",
        null=True,
        blank=True,
        verbose_name="Supervised By",
        help_text="Licensed engineer supervising work",
    )

    # Timing
    scheduled_date = models.DateField(
        verbose_name="Scheduled Date", help_text="Date maintenance was scheduled"
    )
    started_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Started Date/Time",
        help_text="When maintenance work began",
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed Date/Time",
        help_text="When maintenance work was completed",
    )

    # Aircraft State
    pre_maintenance_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Pre-Maintenance Hours",
        help_text="Aircraft hours before maintenance",
    )
    post_maintenance_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Post-Maintenance Hours",
        help_text="Aircraft hours after maintenance",
    )

    # Status and Results
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="scheduled",
        verbose_name="Status",
        help_text="Current maintenance status",
    )
    completion_status = models.CharField(
        max_length=20,
        choices=COMPLETION_STATUS_CHOICES,
        blank=True,
        verbose_name="Completion Status",
        help_text="Result of maintenance work",
    )

    # Documentation
    work_performed = models.TextField(
        verbose_name="Work Performed",
        help_text="Detailed description of work performed",
    )
    parts_used = models.TextField(
        blank=True,
        verbose_name="Parts Used",
        help_text="List of parts and materials used",
    )
    defects_found = models.TextField(
        blank=True,
        verbose_name="Defects Found",
        help_text="Any defects discovered during maintenance",
    )
    corrective_actions = models.TextField(
        blank=True,
        verbose_name="Corrective Actions",
        help_text="Actions taken to correct defects",
    )

    # CASA Compliance
    casa_form_completed = models.BooleanField(
        default=False,
        verbose_name="CASA Form Completed",
        help_text="Required CASA documentation completed",
    )
    return_to_service_authorization = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Return to Service Authorization",
        help_text="Authorization for return to service",
    )

    # Cost Tracking
    labor_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.1"))],
        verbose_name="Labor Hours",
        help_text="Total labor hours for maintenance",
    )
    parts_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Parts Cost",
        help_text="Total cost of parts and materials",
    )

    # Follow-up
    next_maintenance_due = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next Maintenance Due",
        help_text="Date when next maintenance is due",
    )
    followup_required = models.BooleanField(
        default=False,
        verbose_name="Follow-up Required",
        help_text="Requires follow-up maintenance",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"
        ordering = ["-scheduled_date", "-created_at"]

    def __str__(self):
        return f"{self.maintenance_id} - {self.aircraft.registration_mark} ({self.maintenance_type.name})"

    def clean(self):
        """Validate maintenance record requirements"""
        # Completed maintenance must have completion date
        if self.status == "completed" and not self.completed_date:
            raise ValidationError("Completed maintenance must have completion date")

        # Licensed engineer required for certain maintenance types
        if (
            self.maintenance_type.licensed_engineer_required
            and self.status == "completed"
            and not self.supervised_by
        ):
            raise ValidationError(
                f"{self.maintenance_type.name} requires supervision by licensed engineer"
            )

        # CASA form completion check
        if (
            self.maintenance_type.casa_form_required
            and self.status == "completed"
            and not self.casa_form_completed
        ):
            raise ValidationError(
                "CASA form completion required for this maintenance type"
            )

        # Post-maintenance hours validation
        if (
            self.post_maintenance_hours
            and self.post_maintenance_hours < self.pre_maintenance_hours
        ):
            raise ValidationError(
                "Post-maintenance hours cannot be less than pre-maintenance hours"
            )

    @property
    def duration_hours(self):
        """Calculate maintenance duration in hours"""
        if self.started_date and self.completed_date:
            duration = self.completed_date - self.started_date
            return round(duration.total_seconds() / 3600, 2)
        return None

    @property
    def total_cost(self):
        """Calculate total maintenance cost"""
        # This would typically include labor cost calculation
        # For now, just return parts cost
        return self.parts_cost

    @property
    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.status in ["completed", "cancelled"]:
            return False
        return self.scheduled_date < timezone.now().date()

    def save(self, *args, **kwargs):
        """Auto-generate maintenance ID if not provided"""
        if not self.maintenance_id:
            year = timezone.now().year
            # Get next sequence number for this year
            last_record = (
                MaintenanceRecord.objects.filter(
                    maintenance_id__startswith=f"MNT-{year}-"
                )
                .order_by("maintenance_id")
                .last()
            )

            if last_record:
                last_seq = int(last_record.maintenance_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.maintenance_id = f"MNT-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)

    @property
    def rpas_log_entries(self):
        """Get related RPAS Technical Log entries"""
        return self.rpas_entries.all()

    @property
    def is_in_rpas_log(self):
        """Check if this maintenance record is included in RPAS Technical Log"""
        return self.rpas_entries.exists()

    @property
    def rpas_defect_status(self):
        """Get RPAS defect categorization"""
        rpas_entries = self.rpas_entries.all()
        if not rpas_entries:
            return "Not in RPAS Log"

        defect_categories = [entry.defect_category for entry in rpas_entries]
        if "major" in defect_categories:
            return "Major Defect"
        elif "minor" in defect_categories:
            return "Minor Defect"
        else:
            return "No Defect"


class RPASTechnicalLogPartA(models.Model):
    """
    RPAS Technical Log - Part A: Maintenance and Defects
    Company standard form for CASA Part 101 compliance
    References existing maintenance system without duplicating data
    """

    # RPA Identification
    aircraft = models.ForeignKey(
        "aircraft.Aircraft",
        on_delete=models.PROTECT,
        verbose_name="RPA",
        help_text="RPA Aircraft - references existing aircraft data",
    )

    rpa_type_model = models.CharField(
        max_length=100,
        verbose_name="RPA Type & Model",
        help_text="Automatically populated from aircraft data",
        blank=True,
    )

    max_gross_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Max Gross Weight (kg)",
        help_text="Maximum gross weight from aircraft specifications",
        null=True,
        blank=True,
    )

    date_of_registration_expiry = models.DateField(
        verbose_name="Date of Registration Expiry",
        help_text="Aircraft registration expiry date",
        null=True,
        blank=True,
    )

    # Maintenance Schedule
    maintenance_schedule_reference = models.TextField(
        verbose_name="Maintenance Schedule",
        help_text="Reference to manufacturer's maintenance system or Operations Manual",
        blank=True,
    )

    # Part 101 MOC Certification
    part_101_moc_issued_by = models.CharField(
        max_length=100,
        verbose_name="Part 101 MOC Issued By",
        help_text="Authority certifying MOC compliance",
        blank=True,
    )

    part_101_moc_issued_on = models.DateField(
        verbose_name="Part 101 MOC Issued On",
        help_text="Date of MOC certification",
        null=True,
        blank=True,
    )

    part_101_moc_signed_by = models.CharField(
        max_length=100,
        verbose_name="Part 101 MOC Signed By",
        help_text="Name and ARNC of certifying authority",
        blank=True,
    )

    # Maintenance Required Section
    # Links to existing maintenance records rather than duplicating

    # Major Defects Section
    major_defects_notes = models.TextField(
        verbose_name="Major Defects",
        help_text="These defects preclude further flight until rectified",
        blank=True,
    )

    # Minor Defects Section
    minor_defects_notes = models.TextField(
        verbose_name="Minor Defects",
        help_text="These defects must be checked at each Daily Inspection until rectified",
        blank=True,
    )

    # Status and tracking
    current_status = models.CharField(
        max_length=20,
        choices=[
            ("serviceable", "Serviceable"),
            ("unserviceable", "Unserviceable - Major Defects"),
            ("conditional", "Conditional - Minor Defects Only"),
        ],
        default="serviceable",
        verbose_name="Current RPA Status",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        verbose_name="Created By",
        help_text="Staff member who created this log entry",
    )

    class Meta:
        verbose_name = "RPAS Technical Log - Part A"
        verbose_name_plural = "RPAS Technical Log - Part A"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Part A - {self.aircraft.registration_mark} ({self.created_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        """Auto-populate aircraft data to prevent duplication"""
        if self.aircraft:
            self.rpa_type_model = f"{self.aircraft.manufacturer} {self.aircraft.model}"
            self.max_gross_weight = getattr(self.aircraft, "max_takeoff_weight", None)
            # Registration expiry would come from aircraft model if that field exists
        super().save(*args, **kwargs)

    @property
    def linked_maintenance_records(self):
        """Get maintenance records related to this aircraft"""
        return MaintenanceRecord.objects.filter(
            aircraft=self.aircraft, created_at__date=self.created_at.date()
        )

    @property
    def has_major_defects(self):
        """Check if RPA has major defects"""
        return bool(self.major_defects_notes.strip())

    @property
    def has_minor_defects(self):
        """Check if RPA has minor defects"""
        return bool(self.minor_defects_notes.strip())

    @property
    def flight_authorization_status(self):
        """Determine flight authorization status"""
        if self.has_major_defects:
            return "NOT AUTHORIZED - Major Defects"
        elif self.has_minor_defects:
            return "CONDITIONAL - Monitor Minor Defects"
        else:
            return "AUTHORIZED"


class RPASTechnicalLogPartB(models.Model):
    """
    RPAS Technical Log - Part B: Daily Inspection and Time in Service
    Company standard form for daily operations logging
    Integrates with existing flight operations and maintenance
    """

    # Daily Inspection Certification Choices
    SIGNATURE_CHOICES = [
        ("ARN", "ARN - Aviation Reference Number"),
        ("RPC", "RPC - Remote Pilot Certificate"),
    ]

    # Link to Part A for complete record
    technical_log_part_a = models.ForeignKey(
        RPASTechnicalLogPartA,
        on_delete=models.CASCADE,
        related_name="daily_logs",
        verbose_name="Technical Log Part A",
        help_text="Associated Part A record",
    )

    # Daily Inspection Certification
    date = models.DateField(verbose_name="Date", help_text="Date of daily inspection")

    daily_inspection_certification = models.TextField(
        verbose_name="Daily Inspection Certification",
        help_text="Daily inspection certification details (IFP, MC, approved crew member, etc.)",
        blank=True,
    )

    signature_type = models.CharField(
        max_length=3,
        choices=SIGNATURE_CHOICES,
        verbose_name="Signature Type",
        help_text="Type of signature/authorization",
    )

    signature_identifier = models.CharField(
        max_length=20,
        verbose_name="Signature/ARN",
        help_text="ARN number or certificate identifier",
    )

    # RPA Time in Service
    flight_time = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Flight Time",
        help_text="Flight time for this date (hours)",
        default=Decimal("0.00"),
    )

    progressive_total_hrs = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Progressive Total (Hrs)",
        help_text="Running total of flight hours",
        null=True,
        blank=True,
    )

    progressive_total_min = models.PositiveSmallIntegerField(
        verbose_name="Progressive Total (Min)",
        help_text="Additional minutes for precision",
        default=0,
    )

    # Integration with flight operations
    linked_flight_logs = models.ManyToManyField(
        "flight_operations.FlightLog",
        blank=True,
        verbose_name="Linked Flight Logs",
        help_text="Flight logs that contribute to this day's time",
    )

    # Daily Notes
    daily_notes = models.TextField(
        verbose_name="Daily Notes",
        help_text="Additional notes for this daily inspection",
        blank=True,
    )

    # Status
    inspection_satisfactory = models.BooleanField(
        default=True,
        verbose_name="Inspection Satisfactory",
        help_text="Daily inspection completed satisfactorily",
    )

    defects_found = models.TextField(
        verbose_name="Defects Found",
        help_text="Any defects found during daily inspection",
        blank=True,
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        verbose_name="Inspector",
        help_text="Person who performed daily inspection",
    )

    class Meta:
        verbose_name = "RPAS Technical Log - Part B"
        verbose_name_plural = "RPAS Technical Log - Part B"
        ordering = ["-date"]
        unique_together = ["technical_log_part_a", "date"]

    def __str__(self):
        return f"Part B - {self.technical_log_part_a.aircraft.registration_mark} ({self.date})"

    def clean(self):
        """Validate daily inspection data"""
        if not self.inspection_satisfactory and not self.defects_found:
            raise ValidationError(
                "If inspection is not satisfactory, defects must be recorded"
            )

    def save(self, *args, **kwargs):
        """Auto-calculate progressive totals"""
        if not self.progressive_total_hrs:
            # Get previous day's total for this aircraft
            previous_entry = (
                RPASTechnicalLogPartB.objects.filter(
                    technical_log_part_a__aircraft=self.technical_log_part_a.aircraft,
                    date__lt=self.date,
                )
                .order_by("-date")
                .first()
            )

            if previous_entry:
                prev_total_decimal = previous_entry.progressive_total_hrs + (
                    previous_entry.progressive_total_min / 60
                )
                new_total_decimal = prev_total_decimal + self.flight_time
            else:
                new_total_decimal = self.flight_time

            self.progressive_total_hrs = int(new_total_decimal)
            self.progressive_total_min = int((new_total_decimal % 1) * 60)

        super().save(*args, **kwargs)

    @property
    def total_time_formatted(self):
        """Format total time as HH:MM"""
        return f"{int(self.progressive_total_hrs)}:{self.progressive_total_min:02d}"

    @property
    def aircraft(self):
        """Quick access to aircraft"""
        return self.technical_log_part_a.aircraft


class RPASMaintenanceEntry(models.Model):
    """
    Bridge model connecting RPAS Technical Log Part A with existing MaintenanceRecord
    Prevents duplication while maintaining RPAS-specific requirements
    """

    technical_log_part_a = models.ForeignKey(
        RPASTechnicalLogPartA,
        on_delete=models.CASCADE,
        related_name="maintenance_entries",
        verbose_name="RPAS Technical Log Part A",
    )

    maintenance_record = models.ForeignKey(
        MaintenanceRecord,
        on_delete=models.CASCADE,
        related_name="rpas_entries",
        verbose_name="Maintenance Record",
        help_text="Link to existing maintenance record",
    )

    # RPAS-specific maintenance fields that don't exist in MaintenanceRecord
    item_description = models.CharField(
        max_length=200,
        verbose_name="Item",
        help_text="Maintenance item description for RPAS log",
    )

    due_date_tts = models.DateField(
        verbose_name="Due (date or TTS)",
        help_text="Due date or Time To Service",
        null=True,
        blank=True,
    )

    completed_date_arn = models.DateField(
        verbose_name="Completed (date, name, ARN)",
        help_text="Completion date with technician details",
        null=True,
        blank=True,
    )

    completed_by_name = models.CharField(
        max_length=100,
        verbose_name="Completed By (Name)",
        help_text="Name of person who completed maintenance",
        blank=True,
    )

    completed_by_arn = models.CharField(
        max_length=20,
        verbose_name="Completed By (ARN)",
        help_text="ARN of person who completed maintenance",
        blank=True,
    )

    # Defect tracking specific to RPAS requirements
    defect_category = models.CharField(
        max_length=10,
        choices=[
            ("major", "Major Defect"),
            ("minor", "Minor Defect"),
            ("none", "No Defect"),
        ],
        default="none",
        verbose_name="Defect Category",
    )

    rpas_specific_notes = models.TextField(
        verbose_name="RPAS Specific Notes",
        help_text="Additional notes specific to RPAS Technical Log requirements",
        blank=True,
    )

    class Meta:
        verbose_name = "RPAS Maintenance Entry"
        verbose_name_plural = "RPAS Maintenance Entries"
        unique_together = ["technical_log_part_a", "maintenance_record"]

    def __str__(self):
        return f"RPAS Entry: {self.item_description} - {self.maintenance_record.maintenance_id}"

    def save(self, *args, **kwargs):
        """Auto-populate data from linked maintenance record"""
        if self.maintenance_record and not self.completed_by_name:
            # Auto-populate from maintenance record
            self.completed_by_name = (
                self.maintenance_record.performed_by.user.get_full_name()
            )
            # ARN would need to be added to StaffProfile or derived from other fields

        super().save(*args, **kwargs)

    @property
    def maintenance_status(self):
        """Get status from linked maintenance record"""
        return self.maintenance_record.status if self.maintenance_record else "unknown"

    @property
    def is_completed(self):
        """Check if maintenance is completed"""
        return self.maintenance_record and self.maintenance_record.status == "completed"
