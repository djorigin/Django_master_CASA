from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class IncidentType(models.Model):
    """
    CASA Part 101 Incident Type Classifications
    Defines incident categories for RPA operations reporting
    """
    SEVERITY_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('aircraft_failure', 'Aircraft System Failure'),
        ('pilot_error', 'Pilot Error'),
        ('weather', 'Weather Related'),
        ('airspace_infringement', 'Airspace Infringement'),
        ('collision_risk', 'Collision Risk'),
        ('ground_impact', 'Ground Impact/Crash'),
        ('lost_link', 'Lost Communication Link'),
        ('flyaway', 'Aircraft Flyaway'),
        ('battery_failure', 'Battery/Power Failure'),
        ('mechanical', 'Mechanical Failure'),
        ('software', 'Software/Firmware Issue'),
        ('maintenance', 'Maintenance Related'),
        ('ground_operations', 'Ground Operations'),
        ('third_party', 'Third Party Interference'),
        ('other', 'Other'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Incident Type Name",
        help_text="Descriptive name for incident type"
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name="Incident Category",
        help_text="CASA incident classification"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        verbose_name="Severity Level",
        help_text="Risk severity classification"
    )
    
    # CASA Reporting Requirements
    casa_reportable = models.BooleanField(
        default=False,
        verbose_name="CASA Reportable",
        help_text="Must be reported to CASA under Part 101"
    )
    reporting_timeframe_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Reporting Timeframe (Hours)",
        help_text="Maximum hours to report to CASA"
    )
    immediate_notification_required = models.BooleanField(
        default=False,
        verbose_name="Immediate Notification Required",
        help_text="Requires immediate CASA notification"
    )
    
    # Investigation Requirements
    investigation_required = models.BooleanField(
        default=True,
        verbose_name="Investigation Required",
        help_text="Requires formal investigation"
    )
    grounding_required = models.BooleanField(
        default=False,
        verbose_name="Aircraft Grounding Required",
        help_text="Aircraft must be grounded pending investigation"
    )
    
    # Documentation
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of incident type and criteria"
    )
    casa_reference = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CASA Reference",
        help_text="Relevant CASA regulation or advisory material"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incident Type"
        verbose_name_plural = "Incident Types"
        ordering = ['severity', 'category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class IncidentReport(models.Model):
    """
    Individual Incident Reports for RPA Operations
    CASA Part 101 compliant incident reporting and tracking
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_investigation', 'Under Investigation'),
        ('casa_reported', 'Reported to CASA'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]
    
    WEATHER_CONDITIONS_CHOICES = [
        ('vmc', 'Visual Meteorological Conditions (VMC)'),
        ('imc', 'Instrument Meteorological Conditions (IMC)'),
        ('marginal', 'Marginal Weather'),
        ('unknown', 'Unknown'),
    ]

    # Report Identification
    incident_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Incident ID",
        help_text="Unique incident report identifier",
        validators=[
            RegexValidator(
                regex=r'^INC-\d{4}-\d{6}$',
                message="Format: INC-YYYY-XXXXXX"
            )
        ]
    )
    
    # Basic Information
    incident_type = models.ForeignKey(
        IncidentType,
        on_delete=models.PROTECT,
        verbose_name="Incident Type",
        help_text="Type of incident that occurred"
    )
    aircraft = models.ForeignKey(
        'aircraft.Aircraft',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Aircraft Involved",
        help_text="Aircraft involved in incident (if applicable)"
    )
    
    # Personnel
    pilot_in_command = models.ForeignKey(
        'accounts.PilotProfile',
        on_delete=models.PROTECT,
        verbose_name="Pilot in Command",
        help_text="Remote pilot in command during incident"
    )
    reported_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        verbose_name="Reported By",
        help_text="Person who submitted this report"
    )
    
    # Timing and Location
    incident_date = models.DateTimeField(
        verbose_name="Incident Date/Time",
        help_text="Date and time when incident occurred"
    )
    location_description = models.CharField(
        max_length=200,
        verbose_name="Location Description",
        help_text="Description of incident location"
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Incident location latitude (decimal degrees)"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Incident location longitude (decimal degrees)"
    )
    
    # Flight Details
    flight_phase = models.CharField(
        max_length=20,
        choices=[
            ('pre_flight', 'Pre-Flight'),
            ('takeoff', 'Takeoff'),
            ('climb', 'Climb'),
            ('cruise', 'Cruise'),
            ('descent', 'Descent'),
            ('approach', 'Approach'),
            ('landing', 'Landing'),
            ('post_flight', 'Post-Flight'),
            ('ground_ops', 'Ground Operations'),
        ],
        verbose_name="Flight Phase",
        help_text="Phase of flight when incident occurred"
    )
    flight_hours_on_aircraft = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Flight Hours on Aircraft",
        help_text="Total flight hours on aircraft at time of incident"
    )
    
    # Environmental Conditions
    weather_conditions = models.CharField(
        max_length=20,
        choices=WEATHER_CONDITIONS_CHOICES,
        verbose_name="Weather Conditions",
        help_text="Weather conditions at time of incident"
    )
    wind_speed_knots = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Wind Speed (knots)",
        help_text="Wind speed in knots"
    )
    visibility_meters = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Visibility (meters)",
        help_text="Visibility in meters"
    )
    
    # Incident Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Report Status",
        help_text="Current status of incident report"
    )
    summary = models.TextField(
        verbose_name="Incident Summary",
        help_text="Brief summary of what happened"
    )
    detailed_description = models.TextField(
        verbose_name="Detailed Description",
        help_text="Detailed description of incident sequence"
    )
    
    # Damage and Impact
    aircraft_damage = models.TextField(
        blank=True,
        verbose_name="Aircraft Damage",
        help_text="Description of any aircraft damage"
    )
    property_damage = models.TextField(
        blank=True,
        verbose_name="Property Damage",
        help_text="Description of any property damage"
    )
    injuries = models.TextField(
        blank=True,
        verbose_name="Injuries",
        help_text="Description of any injuries"
    )
    
    # Contributing Factors
    contributing_factors = models.TextField(
        verbose_name="Contributing Factors",
        help_text="Factors that contributed to the incident"
    )
    immediate_causes = models.TextField(
        verbose_name="Immediate Causes",
        help_text="Immediate causes of the incident"
    )
    
    # Actions Taken
    immediate_actions = models.TextField(
        verbose_name="Immediate Actions Taken",
        help_text="Actions taken immediately after incident"
    )
    preventive_actions = models.TextField(
        blank=True,
        verbose_name="Preventive Actions",
        help_text="Actions taken to prevent recurrence"
    )
    
    # CASA Reporting
    casa_reported = models.BooleanField(
        default=False,
        verbose_name="Reported to CASA",
        help_text="Incident has been reported to CASA"
    )
    casa_report_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="CASA Report Date",
        help_text="Date/time when reported to CASA"
    )
    casa_reference_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CASA Reference Number",
        help_text="CASA incident reference number"
    )
    
    # Investigation
    investigation_completed = models.BooleanField(
        default=False,
        verbose_name="Investigation Completed",
        help_text="Investigation has been completed"
    )
    investigation_findings = models.TextField(
        blank=True,
        verbose_name="Investigation Findings",
        help_text="Summary of investigation findings"
    )
    investigation_completed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Investigation Completed Date",
        help_text="Date investigation was completed"
    )
    
    # Follow-up
    follow_up_required = models.BooleanField(
        default=False,
        verbose_name="Follow-up Required",
        help_text="Requires follow-up actions"
    )
    follow_up_actions = models.TextField(
        blank=True,
        verbose_name="Follow-up Actions",
        help_text="Required follow-up actions"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"
        ordering = ['-incident_date', '-created_at']

    def __str__(self):
        return f"{self.incident_id} - {self.incident_type.name} ({self.incident_date.strftime('%d/%m/%Y')})"

    def clean(self):
        """Validate incident report requirements"""
        # CASA reportable incidents must be reported within timeframe
        if (self.incident_type.casa_reportable and 
            self.incident_type.reporting_timeframe_hours and
            not self.casa_reported):
            
            hours_since = (timezone.now() - self.incident_date).total_seconds() / 3600
            if hours_since > self.incident_type.reporting_timeframe_hours:
                raise ValidationError(
                    f"CASA reportable incident must be reported within "
                    f"{self.incident_type.reporting_timeframe_hours} hours"
                )
        
        # Closed reports must have investigation completed
        if self.status == 'closed' and not self.investigation_completed:
            raise ValidationError("Cannot close incident without completing investigation")
        
        # Location coordinates validation
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                raise ValidationError("Latitude must be between -90 and 90 degrees")
        
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                raise ValidationError("Longitude must be between -180 and 180 degrees")

    @property
    def is_casa_reportable(self):
        """Check if incident is CASA reportable"""
        return self.incident_type.casa_reportable

    @property
    def is_reporting_overdue(self):
        """Check if CASA reporting is overdue"""
        if not self.is_casa_reportable or self.casa_reported:
            return False
        
        if not self.incident_type.reporting_timeframe_hours:
            return False
        
        hours_since = (timezone.now() - self.incident_date).total_seconds() / 3600
        return hours_since > self.incident_type.reporting_timeframe_hours

    @property
    def days_since_incident(self):
        """Calculate days since incident occurred"""
        return (timezone.now().date() - self.incident_date.date()).days

    def save(self, *args, **kwargs):
        """Auto-generate incident ID if not provided"""
        if not self.incident_id:
            year = timezone.now().year
            # Get next sequence number for this year
            last_report = IncidentReport.objects.filter(
                incident_id__startswith=f'INC-{year}-'
            ).order_by('incident_id').last()
            
            if last_report:
                last_seq = int(last_report.incident_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1
            
            self.incident_id = f'INC-{year}-{next_seq:06d}'
        
        super().save(*args, **kwargs)
