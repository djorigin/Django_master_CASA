from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class Mission(models.Model):
    """
    Mission definition for RPA operations
    CASA Part 101 compliant mission planning and authorization
    """

    MISSION_TYPE_CHOICES = [
        ("commercial", "Commercial Operations"),
        ("training", "Training Operations"),
        ("research", "Research & Development"),
        ("emergency", "Emergency Services"),
        ("surveillance", "Surveillance"),
        ("mapping", "Aerial Mapping"),
        ("inspection", "Infrastructure Inspection"),
        ("delivery", "Delivery Operations"),
        ("photography", "Aerial Photography"),
        ("agricultural", "Agricultural Operations"),
        ("recreational", "Recreational"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("suspended", "Suspended"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("critical", "Critical"),
    ]

    # Mission Identification
    mission_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mission ID",
        help_text="Unique mission identifier",
        validators=[
            RegexValidator(
                regex=r"^MSN-\d{4}-\d{6}$", message="Format: MSN-YYYY-XXXXXX"
            )
        ],
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Mission Name",
        help_text="Descriptive mission name",
    )

    mission_type = models.CharField(
        max_length=20,
        choices=MISSION_TYPE_CHOICES,
        verbose_name="Mission Type",
        help_text="Type of RPA operation",
    )

    # Mission Details
    description = models.TextField(
        verbose_name="Mission Description",
        help_text="Detailed description of mission objectives",
    )

    client = models.ForeignKey(
        "accounts.ClientProfile",
        on_delete=models.PROTECT,
        verbose_name="Client",
        help_text="Client requesting the mission",
    )

    mission_commander = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="commanded_missions",
        verbose_name="Mission Commander",
        help_text="Person responsible for mission oversight",
    )

    # Status and Priority
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        verbose_name="Mission Status",
        help_text="Current mission status",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priority Level",
        help_text="Mission priority level",
    )

    # Scheduling
    planned_start_date = models.DateTimeField(
        verbose_name="Planned Start Date", help_text="Planned mission start date/time"
    )

    planned_end_date = models.DateTimeField(
        verbose_name="Planned End Date", help_text="Planned mission end date/time"
    )

    actual_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Start Date",
        help_text="Actual mission start date/time",
    )

    actual_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual End Date",
        help_text="Actual mission end date/time",
    )

    # CASA Compliance
    casa_authorization_required = models.BooleanField(
        default=False,
        verbose_name="CASA Authorization Required",
        help_text="Mission requires specific CASA authorization",
    )

    casa_authorization_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Authorization Reference",
        help_text="CASA authorization or exemption reference",
    )

    # Risk Assessment
    risk_assessment_completed = models.BooleanField(
        default=False,
        verbose_name="Risk Assessment Completed",
        help_text="Risk assessment has been completed",
    )

    risk_level = models.CharField(
        max_length=10,
        choices=[
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
            ("critical", "Critical Risk"),
        ],
        blank=True,
        verbose_name="Risk Level",
        help_text="Assessed risk level",
    )

    # Documentation
    briefing_notes = models.TextField(
        blank=True,
        verbose_name="Briefing Notes",
        help_text="Mission briefing notes and considerations",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"
        ordering = ["-planned_start_date"]

    def __str__(self):
        return f"{self.mission_id} - {self.name}"

    def clean(self):
        """Validate mission parameters"""
        if self.planned_end_date <= self.planned_start_date:
            raise ValidationError("End date must be after start date")

        if (
            self.actual_start_date
            and self.actual_end_date
            and self.actual_end_date <= self.actual_start_date
        ):
            raise ValidationError("Actual end date must be after actual start date")

    @property
    def is_active(self):
        """Check if mission is currently active"""
        return self.status == "active"

    @property
    def duration_planned(self):
        """Calculate planned mission duration"""
        return self.planned_end_date - self.planned_start_date

    @property
    def duration_actual(self):
        """Calculate actual mission duration"""
        if self.actual_start_date and self.actual_end_date:
            return self.actual_end_date - self.actual_start_date
        return None

    def save(self, *args, **kwargs):
        """Auto-generate mission ID if not provided"""
        if not self.mission_id:
            year = timezone.now().year
            last_mission = (
                Mission.objects.filter(mission_id__startswith=f"MSN-{year}-")
                .order_by("mission_id")
                .last()
            )

            if last_mission:
                last_seq = int(last_mission.mission_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.mission_id = f"MSN-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)


class FlightPlan(models.Model):
    """
    Individual Flight Plan for RPA Operations
    CASA Part 101 compliant flight planning
    """

    FLIGHT_TYPE_CHOICES = [
        ("line_of_sight", "Visual Line of Sight (VLOS)"),
        ("extended_vlos", "Extended Visual Line of Sight (EVLOS)"),
        ("beyond_vlos", "Beyond Visual Line of Sight (BVLOS)"),
        ("night_operations", "Night Operations"),
        ("controlled_airspace", "Controlled Airspace Operations"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted for Approval"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # Flight Plan Identification
    flight_plan_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Flight Plan ID",
        help_text="Unique flight plan identifier",
        validators=[
            RegexValidator(
                regex=r"^FPL-\d{4}-\d{6}$", message="Format: FPL-YYYY-XXXXXX"
            )
        ],
    )

    # Related Objects
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        verbose_name="Mission",
        help_text="Associated mission",
    )

    aircraft = models.ForeignKey(
        "aircraft.Aircraft",
        on_delete=models.PROTECT,
        verbose_name="Aircraft",
        help_text="Aircraft for this flight",
    )

    pilot_in_command = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.PROTECT,
        related_name="commanded_flights",
        verbose_name="Pilot in Command",
        help_text="Remote pilot in command",
    )

    remote_pilot_observer = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.PROTECT,
        related_name="observed_flights",
        null=True,
        blank=True,
        verbose_name="Remote Pilot Observer",
        help_text="Observer pilot (if required)",
    )

    # Flight Details
    flight_type = models.CharField(
        max_length=20,
        choices=FLIGHT_TYPE_CHOICES,
        verbose_name="Flight Type",
        help_text="Type of flight operation",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Status",
        help_text="Current flight plan status",
    )

    # Operational Area
    operational_area = models.ForeignKey(
        "airspace.OperationalArea",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Operational Area",
        help_text="Defined operational area (if applicable)",
    )

    departure_location = models.CharField(
        max_length=200,
        verbose_name="Departure Location",
        help_text="Departure location description",
    )

    departure_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Departure Latitude",
        help_text="Departure latitude in decimal degrees",
    )

    departure_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Departure Longitude",
        help_text="Departure longitude in decimal degrees",
    )

    # Flight Parameters
    planned_altitude_agl = models.PositiveIntegerField(
        verbose_name="Planned Altitude AGL (feet)",
        help_text="Planned operating altitude above ground level",
        validators=[MaxValueValidator(400)],  # Part 101 standard limit
    )

    maximum_range_from_pilot = models.PositiveIntegerField(
        verbose_name="Maximum Range from Pilot (meters)",
        help_text="Maximum distance from remote pilot",
        validators=[MaxValueValidator(500)],  # VLOS limit
    )

    # Timing
    planned_departure_time = models.DateTimeField(
        verbose_name="Planned Departure Time", help_text="Planned flight departure time"
    )

    estimated_flight_time = models.DurationField(
        verbose_name="Estimated Flight Time", help_text="Estimated duration of flight"
    )

    actual_departure_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Departure Time",
        help_text="Actual flight departure time",
    )

    actual_landing_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Landing Time",
        help_text="Actual flight landing time",
    )

    # Weather and Conditions
    weather_minimums = models.TextField(
        verbose_name="Weather Minimums",
        help_text="Minimum weather conditions for flight",
    )

    planned_weather_check_time = models.DateTimeField(
        verbose_name="Planned Weather Check Time",
        help_text="When weather will be checked before flight",
    )

    # CASA Compliance
    notam_checked = models.BooleanField(
        default=False,
        verbose_name="NOTAM Checked",
        help_text="NOTAMs have been checked",
    )

    airspace_coordination_required = models.BooleanField(
        default=False,
        verbose_name="Airspace Coordination Required",
        help_text="Requires coordination with ATC or other authorities",
    )

    airspace_coordination_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Airspace Coordination Reference",
        help_text="ATC clearance or coordination reference",
    )

    # Safety
    emergency_procedures = models.TextField(
        verbose_name="Emergency Procedures",
        help_text="Emergency procedures for this flight",
    )

    lost_link_procedures = models.TextField(
        verbose_name="Lost Link Procedures",
        help_text="Procedures if communication link is lost",
    )

    # Route Planning (JSON format for waypoints)
    route_waypoints = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Route Waypoints",
        help_text="Flight route waypoints in JSON format",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flight Plan"
        verbose_name_plural = "Flight Plans"
        ordering = ["-planned_departure_time"]

    def __str__(self):
        return f"{self.flight_plan_id} - {self.aircraft.registration_mark}"

    def clean(self):
        """Validate flight plan parameters"""
        # Validate coordinates
        if not (-90 <= self.departure_latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees")

        if not (-180 <= self.departure_longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees")

        # Validate altitude for flight type
        if self.flight_type == "line_of_sight" and self.planned_altitude_agl > 120:
            raise ValidationError("VLOS operations typically limited to 120ft AGL")

        # Validate range for VLOS
        if self.flight_type == "line_of_sight" and self.maximum_range_from_pilot > 500:
            raise ValidationError("VLOS operations limited to 500m from pilot")

    @property
    def is_completed(self):
        """Check if flight is completed"""
        return self.status == "completed"

    @property
    def actual_flight_duration(self):
        """Calculate actual flight duration"""
        if self.actual_departure_time and self.actual_landing_time:
            return self.actual_landing_time - self.actual_departure_time
        return None

    def save(self, *args, **kwargs):
        """Auto-generate flight plan ID if not provided"""
        if not self.flight_plan_id:
            year = timezone.now().year
            last_plan = (
                FlightPlan.objects.filter(flight_plan_id__startswith=f"FPL-{year}-")
                .order_by("flight_plan_id")
                .last()
            )

            if last_plan:
                last_seq = int(last_plan.flight_plan_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.flight_plan_id = f"FPL-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)


class FlightLog(models.Model):
    """
    Flight Log Entry for completed flights
    CASA Part 101 compliant flight record keeping
    """

    LOG_ENTRY_CHOICES = [
        ("normal", "Normal Flight"),
        ("training", "Training Flight"),
        ("test", "Test Flight"),
        ("maintenance_test", "Maintenance Test Flight"),
        ("emergency_return", "Emergency Return"),
        ("incident", "Incident Flight"),
    ]

    # Log Identification
    log_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Log ID",
        help_text="Unique flight log identifier",
        validators=[
            RegexValidator(
                regex=r"^LOG-\d{4}-\d{6}$", message="Format: LOG-YYYY-XXXXXX"
            )
        ],
    )

    # Related Objects
    flight_plan = models.OneToOneField(
        FlightPlan,
        on_delete=models.CASCADE,
        verbose_name="Flight Plan",
        help_text="Associated flight plan",
    )

    # Flight Performance
    takeoff_time = models.DateTimeField(
        verbose_name="Takeoff Time", help_text="Actual takeoff time"
    )

    landing_time = models.DateTimeField(
        verbose_name="Landing Time", help_text="Actual landing time"
    )

    flight_time = models.DurationField(
        verbose_name="Flight Time", help_text="Total flight time"
    )

    maximum_altitude_achieved = models.PositiveIntegerField(
        verbose_name="Maximum Altitude Achieved (feet AGL)",
        help_text="Highest altitude reached during flight",
    )

    maximum_range_achieved = models.PositiveIntegerField(
        verbose_name="Maximum Range Achieved (meters)",
        help_text="Furthest distance from takeoff point",
    )

    # Aircraft Performance
    pre_flight_battery_voltage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Pre-flight Battery Voltage",
        help_text="Battery voltage before flight",
    )

    post_flight_battery_voltage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Post-flight Battery Voltage",
        help_text="Battery voltage after flight",
    )

    # Weather Conditions
    wind_speed_takeoff = models.PositiveIntegerField(
        verbose_name="Wind Speed at Takeoff (knots)",
        help_text="Wind speed at takeoff",
    )

    wind_direction_takeoff = models.PositiveIntegerField(
        verbose_name="Wind Direction at Takeoff (degrees)",
        help_text="Wind direction at takeoff",
        validators=[MaxValueValidator(360)],
    )

    temperature_celsius = models.IntegerField(
        verbose_name="Temperature (°C)", help_text="Temperature during flight"
    )

    visibility_meters = models.PositiveIntegerField(
        verbose_name="Visibility (meters)", help_text="Visibility during flight"
    )

    # Flight Details
    log_entry_type = models.CharField(
        max_length=20,
        choices=LOG_ENTRY_CHOICES,
        default="normal",
        verbose_name="Log Entry Type",
        help_text="Type of flight log entry",
    )

    objectives_achieved = models.BooleanField(
        default=True,
        verbose_name="Objectives Achieved",
        help_text="Flight objectives were achieved",
    )

    # Issues and Observations
    technical_issues = models.TextField(
        blank=True,
        verbose_name="Technical Issues",
        help_text="Any technical issues encountered",
    )

    weather_issues = models.TextField(
        blank=True,
        verbose_name="Weather Issues",
        help_text="Any weather-related issues",
    )

    operational_notes = models.TextField(
        blank=True,
        verbose_name="Operational Notes",
        help_text="General operational notes and observations",
    )

    lessons_learned = models.TextField(
        blank=True,
        verbose_name="Lessons Learned",
        help_text="Lessons learned from this flight",
    )

    # Pilot Assessment
    pilot_performance_notes = models.TextField(
        blank=True,
        verbose_name="Pilot Performance Notes",
        help_text="Notes on pilot performance (for training flights)",
    )

    # CASA Compliance
    regulatory_compliance_notes = models.TextField(
        blank=True,
        verbose_name="Regulatory Compliance Notes",
        help_text="Notes on regulatory compliance during flight",
    )

    # Data Collection
    data_collected = models.TextField(
        blank=True,
        verbose_name="Data Collected",
        help_text="Description of data/imagery collected",
    )

    file_references = models.TextField(
        blank=True,
        verbose_name="File References",
        help_text="References to collected files, images, or data",
    )

    # Maintenance
    maintenance_required = models.BooleanField(
        default=False,
        verbose_name="Maintenance Required",
        help_text="Aircraft requires maintenance after this flight",
    )

    maintenance_notes = models.TextField(
        blank=True,
        verbose_name="Maintenance Notes",
        help_text="Notes for maintenance personnel",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flight Log"
        verbose_name_plural = "Flight Logs"
        ordering = ["-takeoff_time"]

    def __str__(self):
        return f"{self.log_id} - {self.flight_plan.aircraft.registration_mark} ({self.takeoff_time.strftime('%d/%m/%Y')})"

    def clean(self):
        """Validate flight log parameters"""
        if self.landing_time <= self.takeoff_time:
            raise ValidationError("Landing time must be after takeoff time")

        # Calculate and validate flight time
        calculated_time = self.landing_time - self.takeoff_time
        if abs((calculated_time - self.flight_time).total_seconds()) > 60:
            raise ValidationError("Flight time doesn't match takeoff/landing times")

    @property
    def total_flight_hours(self):
        """Get flight time in decimal hours"""
        return self.flight_time.total_seconds() / 3600

    @property
    def average_ground_speed(self):
        """Calculate average ground speed if range data available"""
        if self.maximum_range_achieved and self.flight_time:
            # Simple calculation - could be enhanced with route data
            distance_km = self.maximum_range_achieved / 1000
            time_hours = self.flight_time.total_seconds() / 3600
            return distance_km / time_hours if time_hours > 0 else 0
        return None

    def save(self, *args, **kwargs):
        """Auto-generate log ID if not provided"""
        if not self.log_id:
            year = timezone.now().year
            last_log = (
                FlightLog.objects.filter(log_id__startswith=f"LOG-{year}-")
                .order_by("log_id")
                .last()
            )

            if last_log:
                last_seq = int(last_log.log_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.log_id = f"LOG-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)
