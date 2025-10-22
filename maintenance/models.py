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
