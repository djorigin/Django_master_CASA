from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class AircraftType(models.Model):
    """
    CASA Part 101 Aircraft Type Classifications
    Defines aircraft categories and operational limitations
    """
    CATEGORY_CHOICES = [
        ('excluded', 'Excluded Category (Part 101.073)'),
        ('micro', 'Micro RPA (≤250g)'),
        ('small', 'Small RPA (>250g ≤25kg)'),  
        ('medium', 'Medium RPA (>25kg ≤150kg)'),
        ('large', 'Large RPA (>150kg)'),
    ]
    
    OPERATION_TYPE_CHOICES = [
        ('recreational', 'Recreational'),
        ('commercial', 'Commercial'),
        ('research', 'Research & Development'),
        ('emergency', 'Emergency Services'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Aircraft Type Name",
        help_text="Manufacturer and model designation"
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Manufacturer",
        help_text="Aircraft manufacturer name"
    )
    model = models.CharField(
        max_length=100,
        verbose_name="Model",
        help_text="Aircraft model designation"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="CASA Category",
        help_text="Part 101 operational category"
    )
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name="Operation Type",
        help_text="Authorized operation type"
    )
    
    # Technical Specifications
    maximum_takeoff_weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        verbose_name="MTOW (kg)",
        help_text="Maximum Takeoff Weight in kilograms"
    )
    maximum_operating_height = models.PositiveIntegerField(
        verbose_name="Maximum Operating Height (ft AGL)",
        help_text="Maximum operating height above ground level"
    )
    maximum_speed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Speed (knots)",
        help_text="Maximum operating speed in knots"
    )
    
    # CASA Compliance Fields
    casa_type_certificate = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CASA Type Certificate",
        help_text="CASA type certificate number if applicable"
    )
    excluded_category_compliant = models.BooleanField(
        default=False,
        verbose_name="Excluded Category Compliant",
        help_text="Meets Part 101.073 excluded category requirements"
    )
    
    # Documentation
    flight_manual_required = models.BooleanField(
        default=True,
        verbose_name="Flight Manual Required",
        help_text="Aircraft requires approved flight manual"
    )
    maintenance_manual_required = models.BooleanField(
        default=True,
        verbose_name="Maintenance Manual Required",
        help_text="Aircraft requires maintenance manual"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aircraft Type"
        verbose_name_plural = "Aircraft Types"
        ordering = ['manufacturer', 'model']

    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.get_category_display()})"

    def clean(self):
        """Validate CASA compliance requirements"""
        # Validate excluded category requirements (Part 101.073)
        if self.category == 'excluded':
            if self.maximum_takeoff_weight > 25:
                raise ValidationError("Excluded category aircraft must be ≤25kg MTOW")
            if self.maximum_operating_height > 400:
                raise ValidationError("Excluded category limited to 400ft AGL")
            self.excluded_category_compliant = True
        
        # Validate micro RPA requirements
        if self.category == 'micro':
            if self.maximum_takeoff_weight > 0.25:
                raise ValidationError("Micro RPA must be ≤250g")
        
        # Commercial operations require type certificate for larger aircraft
        if self.operation_type == 'commercial' and self.category in ['medium', 'large']:
            if not self.casa_type_certificate:
                raise ValidationError("Commercial medium/large RPA require CASA type certificate")


class Aircraft(models.Model):
    """
    Individual Aircraft Registration and Configuration
    CASA Part 101 compliant aircraft records
    """
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('pending', 'Registration Pending'),
        ('suspended', 'Suspended'),
        ('deregistered', 'Deregistered'),
    ]

    # Registration Details
    registration_mark = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Registration Mark",
        help_text="Aircraft registration identifier",
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]{3,20}$',
                message="Registration mark must be 3-20 alphanumeric characters"
            )
        ]
    )
    aircraft_type = models.ForeignKey(
        AircraftType,
        on_delete=models.PROTECT,
        verbose_name="Aircraft Type",
        help_text="CASA approved aircraft type"
    )
    
    # Owner Information (linked to accounts app)
    owner = models.ForeignKey(
        'accounts.ClientProfile',
        on_delete=models.PROTECT,
        verbose_name="Aircraft Owner",
        help_text="Registered owner from client profiles"
    )
    operator = models.ForeignKey(
        'accounts.ClientProfile',
        on_delete=models.PROTECT,
        related_name='operated_aircraft',
        verbose_name="Aircraft Operator",
        help_text="Current operator (may differ from owner)",
        null=True,
        blank=True
    )
    
    # Aircraft Details
    serial_number = models.CharField(
        max_length=50,
        verbose_name="Serial Number",
        help_text="Manufacturer's serial number"
    )
    year_manufactured = models.PositiveIntegerField(
        verbose_name="Year Manufactured",
        help_text="Year aircraft was manufactured"
    )
    
    # Operational Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Registration Status",
        help_text="Current CASA registration status"
    )
    airworthiness_valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Airworthiness Valid Until",
        help_text="Certificate of airworthiness expiry date"
    )
    
    # Insurance and Compliance
    insurance_valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Insurance Valid Until",
        help_text="Insurance coverage expiry date"
    )
    last_maintenance_check = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Maintenance Check",
        help_text="Date of last maintenance inspection"
    )
    next_maintenance_due = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next Maintenance Due",
        help_text="Date next maintenance is due"
    )
    
    # Operational Limitations
    current_flight_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Current Flight Hours",
        help_text="Total accumulated flight hours"
    )
    maximum_flight_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Flight Hours",
        help_text="Maximum approved flight hours before overhaul"
    )
    
    # Documentation
    flight_manual_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Flight Manual Reference",
        help_text="Flight manual document reference"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Additional aircraft notes and observations"
    )
    
    # Metadata
    registration_date = models.DateField(
        default=timezone.now,
        verbose_name="Registration Date",
        help_text="Date aircraft was registered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aircraft"
        verbose_name_plural = "Aircraft"
        ordering = ['registration_mark']

    def __str__(self):
        return f"{self.registration_mark} - {self.aircraft_type.manufacturer} {self.aircraft_type.model}"

    def clean(self):
        """Validate aircraft compliance and operational requirements"""
        # Ensure operator is specified for commercial operations
        if self.aircraft_type.operation_type == 'commercial' and not self.operator:
            raise ValidationError("Commercial aircraft must have designated operator")
        
        # Validate airworthiness for non-excluded category
        if self.aircraft_type.category != 'excluded' and not self.airworthiness_valid_until:
            raise ValidationError("Non-excluded category aircraft require airworthiness certificate")
        
        # Check maintenance due dates
        if self.next_maintenance_due and self.next_maintenance_due < timezone.now().date():
            raise ValidationError("Aircraft maintenance is overdue")

    @property
    def is_airworthy(self):
        """Check if aircraft airworthiness is current"""
        if not self.airworthiness_valid_until:
            return self.aircraft_type.category == 'excluded'
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
            return 'unknown'
        
        days_until_due = (self.next_maintenance_due - timezone.now().date()).days
        
        if days_until_due < 0:
            return 'overdue'
        elif days_until_due <= 7:
            return 'due_soon'
        else:
            return 'current'

    @property
    def is_operational(self):
        """Check if aircraft is operational (airworthy, insured, maintenance current)"""
        return (
            self.status == 'registered' and
            self.is_airworthy and
            self.is_insured and
            self.maintenance_status in ['current', 'due_soon']
        )
