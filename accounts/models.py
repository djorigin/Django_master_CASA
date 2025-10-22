from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .utils import profile_photo_upload_path

# Validators
phone_validator = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Administrator"),
        ("staff", "Staff Member"),
        ("client", "Client"),
        ("pilot", "Pilot"),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name

    @property
    def full_name(self):
        """Property for easy access to full name."""
        return self.get_full_name()


class StaffProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ("operations", "Operations"),
        ("admin", "Administration"),
        ("hr", "Human Resources"),
        ("finance", "Finance"),
        ("technical", "Technical"),
        ("sales", "Sales & Marketing"),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="staff_profile"
    )
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    position_title = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField(
        max_length=500
    )  # Changed to TextField for better formatting
    photo_id = models.ImageField(upload_to="staff_ids/%Y/%m/", blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"
        ordering = ["user__last_name", "user__first_name"]

    def clean(self):
        if self.user.role != "staff":
            raise ValidationError("Linked user must have role 'staff'.")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position_title}"


class PilotProfile(models.Model):
    ROLE_CHOICES = [
        ("chief_remote_pilot", "Chief Remote Pilot"),
        ("remote_pilot", "Remote Pilot"),
    ]

    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("on_mission", "On Mission"),
        ("unavailable", "Unavailable"),
        ("maintenance", "Equipment Maintenance"),
        ("training", "In Training"),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="pilot_profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    arn = models.CharField(
        "ARN Number", max_length=20, unique=True, help_text="Aviation Reference Number"
    )
    repl_number = models.CharField(
        "REPL Number",
        max_length=20,
        blank=True,
        null=True,
        help_text="Remote Pilot License Number",
    )
    repl_expiry = models.DateField("REPL Expiry Date", blank=True, null=True)
    medical_clearance_date = models.DateField(blank=True, null=True)
    certifications = models.TextField(
        blank=True, help_text="List additional certifications"
    )
    availability_status = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="available"
    )
    home_base_location = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(
        max_length=20, blank=True, validators=[phone_validator]
    )
    contact_number = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField(max_length=500)
    photo_id = models.ImageField(upload_to="pilot_ids/%Y/%m/", blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pilot Profile"
        verbose_name_plural = "Pilot Profiles"
        ordering = ["role", "user__last_name", "user__first_name"]

    def clean(self):
        if self.user.role != "pilot":
            raise ValidationError("Linked user must have role 'pilot'.")

        # Check if REPL is expired
        if self.repl_expiry and self.repl_expiry < timezone.now().date():
            raise ValidationError("REPL license has expired.")

    @property
    def is_repl_expired(self):
        """Check if REPL license is expired."""
        if self.repl_expiry:
            return self.repl_expiry < timezone.now().date()
        return None

    @property
    def is_available(self):
        """Check if pilot is available for missions."""
        return self.availability_status == "available" and not self.is_repl_expired

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"


class OperatorCertificate(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("suspended", "Suspended"),
        ("cancelled", "Cancelled"),
    ]

    reoc_number = models.CharField(
        "REOC Number",
        max_length=50,
        unique=True,
        help_text="Remote Operator Certificate Number",
    )
    company_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    casa_operator_number = models.CharField(
        "CASA Operator Number", max_length=50, blank=True, null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Operator Certificate"
        verbose_name_plural = "Operator Certificates"
        ordering = ["-issue_date"]

    def clean(self):
        if self.expiry_date <= self.issue_date:
            raise ValidationError("Expiry date must be after issue date.")

    @property
    def is_expired(self):
        """Check if certificate is expired."""
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        """Calculate days until certificate expires."""
        today = timezone.now().date()
        if self.expiry_date > today:
            return (self.expiry_date - today).days
        return 0

    def __str__(self):
        return f"{self.company_name} - {self.reoc_number}"


class ClientProfile(models.Model):
    INDUSTRY_CHOICES = [
        ("agriculture", "Agriculture"),
        ("construction", "Construction"),
        ("energy", "Energy & Utilities"),
        ("entertainment", "Entertainment & Media"),
        ("environmental", "Environmental"),
        ("insurance", "Insurance"),
        ("mining", "Mining"),
        ("real_estate", "Real Estate"),
        ("security", "Security & Surveillance"),
        ("surveying", "Surveying & Mapping"),
        ("other", "Other"),
    ]

    CLIENT_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
        ("suspended", "Suspended"),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="client_profile"
    )
    company_name = models.CharField(max_length=100)
    abn = models.CharField(
        "ABN",
        max_length=20,
        blank=True,
        null=True,
        help_text="Australian Business Number",
    )
    contact_number = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField(max_length=500)
    billing_email = models.EmailField()
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, blank=True)
    account_manager = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_clients",
    )
    status = models.CharField(
        max_length=20, choices=CLIENT_STATUS_CHOICES, default="prospect"
    )
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_terms = models.PositiveIntegerField(
        default=30, help_text="Payment terms in days"
    )
    notes = models.TextField(blank=True)
    photo_id = models.ImageField(upload_to="client_ids/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"
        ordering = ["company_name", "user__last_name"]

    def clean(self):
        if self.user.role != "client":
            raise ValidationError("Linked user must have role 'client'.")

    @property
    def is_active(self):
        """Check if client is active."""
        return self.status == "active"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"


class CompanyContactDetails(models.Model):
    """
    Singleton model for company contact details and organizational information.
    Only one instance should exist in the database.
    """

    # Contact Information
    legal_entity_name = models.CharField(
        max_length=200,
        verbose_name="Name of Legal Entity",
        help_text="Official registered legal name of the company",
    )
    trading_name = models.CharField(
        max_length=200,
        verbose_name="Trading Name",
        help_text="Business trading name (if different from legal name)",
        blank=True,
    )

    # Registered Office
    registered_office_address = models.TextField(
        verbose_name="Registered Office Address",
        help_text="Full registered office address including postcode",
    )

    # Registration Numbers
    arn = models.CharField(
        max_length=20,
        verbose_name="ARN",
        help_text="Aviation Reference Number",
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]{6,20}$",
                message="ARN must be 6-20 alphanumeric characters",
            )
        ],
    )
    abn = models.CharField(
        max_length=15,
        verbose_name="ABN",
        help_text="Australian Business Number",
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message="ABN must be 11 digits",
            )
        ],
    )

    # Operational Headquarters
    operational_hq_address = models.TextField(
        verbose_name="Operational Headquarters Address",
        help_text="Physical address of operational headquarters",
    )
    operational_hq_phone = models.CharField(
        max_length=20,
        verbose_name="Operations Headquarters Phone",
        validators=[phone_validator],
    )
    operational_hq_email = models.EmailField(
        verbose_name="Operational Headquarters Email",
        help_text="Main operational contact email",
    )

    # Organizational Overview
    organizational_overview = models.TextField(
        verbose_name="Organisational Overview",
        help_text="Description of the company's operations and specialties",
        default=(
            "{Legal Entity Name} is an entity that holds a remotely piloted aircraft "
            "operator's certificate (ReOC) to conduct aerial work activities in remotely "
            "piloted aircraft systems (RPAS). {Legal Entity Name} specialises in aerial "
            "survey operations over mine sites utilising the RPA listed in operational "
            "documentation. Remote pilots and ground crew are employed on a full-time, "
            "part-time or casual basis depending on demand and level of activity. "
            "Maintenance is subcontracted to various organisations as required."
        ),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Last Updated By",
        help_text="User who last updated these details",
    )

    class Meta:
        verbose_name = "Company Contact Details"
        verbose_name_plural = "Company Contact Details"

    def save(self, *args, **kwargs):
        """
        Ensure only one instance exists (Singleton pattern).
        Invalidate cache when data changes.
        """
        if CompanyContactDetails.objects.exists() and not self.pk:
            raise ValidationError(
                "Only one Company Contact Details record is allowed. "
                "Please edit the existing record."
            )
        super().save(*args, **kwargs)

        # Invalidate all cached company details when data changes
        cache.delete_many(
            [
                "company_details",
                "company_display_name",
                "company_legal_name",
                "company_arn",
                "company_full_info",
            ]
        )

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance, create if doesn't exist.
        """
        instance, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "legal_entity_name": "Your Company Name",
                "trading_name": "",
                "registered_office_address": "Enter your registered address",
                "arn": "ARN000000",
                "abn": "00000000000",
                "operational_hq_address": "Enter your operational address",
                "operational_hq_phone": "+61000000000",
                "operational_hq_email": "operations@yourcompany.com.au",
            },
        )
        return instance

    @property
    def display_name(self):
        """Return the trading name if available, otherwise legal name."""
        return self.trading_name if self.trading_name else self.legal_entity_name

    def get_formatted_overview(self):
        """
        Return organizational overview with placeholders replaced.
        """
        return self.organizational_overview.replace(
            "{Legal Entity Name}", self.legal_entity_name
        ).replace("{Trading Name}", self.display_name)

    def __str__(self):
        return f"Company Details: {self.display_name}"


class KeyPersonnel(models.Model):
    """
    Singleton model for CASA key personnel information.
    Uses ForeignKey relationships to existing vetted data models for data security and integrity.
    Only one instance should exist in the database per CASA regulations.
    """

    # Chief Remote Pilot - ForeignKey to PilotProfile (already vetted pilot data)
    chief_remote_pilot = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Chief Remote Pilot",
        help_text="Select from existing pilot profiles - must be CASA approved",
        related_name="chief_remote_pilot_assignments",
    )
    chief_remote_pilot_approved_date = models.DateField(
        verbose_name="Chief Remote Pilot Approval Date",
        help_text="Date approved by CASA for this key position",
        null=True,
        blank=True,
    )

    # Maintenance Controller - ForeignKey to StaffProfile (already vetted staff data)
    maintenance_controller = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Maintenance Controller",
        help_text="Select from existing staff profiles - must be qualified for maintenance control",
        related_name="maintenance_controller_assignments",
    )
    maintenance_controller_approved_date = models.DateField(
        verbose_name="Maintenance Controller Approval Date",
        help_text="Date approved by CASA for this key position",
        null=True,
        blank=True,
    )

    # CEO - ForeignKey to StaffProfile (already vetted staff data)
    ceo = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Chief Executive Officer",
        help_text="Select from existing staff profiles - must be authorized CEO",
        related_name="ceo_assignments",
    )
    ceo_approved_date = models.DateField(
        verbose_name="CEO Approval Date",
        help_text="Date approved by CASA for this key position",
        null=True,
        blank=True,
    )

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Key Personnel"
        verbose_name_plural = "Key Personnel"

    def save(self, *args, **kwargs):
        """Singleton pattern - only allow one instance."""
        if not self.pk and KeyPersonnel.objects.exists():
            # If trying to create a new instance and one already exists, update the existing one
            existing = KeyPersonnel.objects.first()
            self.pk = existing.pk

        super().save(*args, **kwargs)

        # Clear cache when key personnel information changes
        cache.delete("key_personnel_cache")

    @classmethod
    def load(cls):
        """
        Singleton loader - returns the single instance or creates one if it doesn't exist.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_vacant_positions(self):
        """
        Return a list of vacant key personnel positions.
        CASA requires all positions to be filled.
        """
        vacant = []

        if not self.chief_remote_pilot:
            vacant.append("Chief Remote Pilot")

        if not self.maintenance_controller:
            vacant.append("Maintenance Controller")

        if not self.ceo:
            vacant.append("CEO")

        return vacant

    def is_casa_compliant(self):
        """
        Check if all required key personnel positions are filled.
        Returns True if compliant, False if any positions are vacant.
        """
        return len(self.get_vacant_positions()) == 0

    def get_personnel_summary(self):
        """
        Return a dictionary summary of all key personnel using existing vetted data.
        """
        return {
            "chief_remote_pilot": {
                "name": (
                    self.chief_remote_pilot.user.get_full_name()
                    if self.chief_remote_pilot
                    else "VACANT"
                ),
                "arn": (
                    self.chief_remote_pilot.license_number
                    if self.chief_remote_pilot
                    else "N/A"
                ),
                "approved_date": self.chief_remote_pilot_approved_date,
                "profile": self.chief_remote_pilot,
            },
            "maintenance_controller": {
                "name": (
                    self.maintenance_controller.user.get_full_name()
                    if self.maintenance_controller
                    else "VACANT"
                ),
                "employee_id": (
                    self.maintenance_controller.employee_id
                    if self.maintenance_controller
                    else "N/A"
                ),
                "approved_date": self.maintenance_controller_approved_date,
                "profile": self.maintenance_controller,
            },
            "ceo": {
                "name": self.ceo.user.get_full_name() if self.ceo else "VACANT",
                "employee_id": self.ceo.employee_id if self.ceo else "N/A",
                "approved_date": self.ceo_approved_date,
                "profile": self.ceo,
            },
        }

    def __str__(self):
        vacant_count = len(self.get_vacant_positions())
        if vacant_count == 0:
            return "Key Personnel: All positions filled"
        else:
            return f"Key Personnel: {vacant_count} position(s) vacant"
