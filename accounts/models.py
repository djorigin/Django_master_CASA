from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError


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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('client', 'Client'),
        ('pilot', 'Pilot'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    position_title = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    photo_id = models.ImageField(upload_to='staff_ids/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position_title}"

class PilotProfile(models.Model):
    ROLE_CHOICES = (
        ('chief_remote_pilot', 'Chief Remote Pilot'),
        ('remote_pilot', 'Remote Pilot'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    arn = models.CharField(max_length=20, unique=True)
    repl_number = models.CharField(max_length=20, blank=True, null=True)
    repl_expiry = models.DateField(blank=True, null=True)
    medical_clearance_date = models.DateField(blank=True, null=True)
    certifications = models.TextField(blank=True)
    availability_status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('on_mission', 'On Mission'),
        ('unavailable', 'Unavailable'),
    ], default='available')
    home_base_location = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    photo_id = models.ImageField(upload_to='pilot_ids/', blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

class OperatorCertificate(models.Model):
    reoc_number = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    issue_date = models.DateField()
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.company_name} - {self.reoc_number}"
    

class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    billing_email = models.EmailField()
    industry = models.CharField(max_length=100, blank=True)
    account_manager = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    photo_id = models.ImageField(upload_to='client_ids/', blank=True, null=True)

    def clean(self):
        if self.user.role != 'client':
            raise ValidationError("Linked user must have role 'client'.")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"
