# User Management

## Overview

The CASA Master Project uses a custom user model with role-based access control. Users can have one of three roles: Staff, Client, or Pilot.

## User Roles

### Staff
Staff members have administrative and operational responsibilities within the organization.

**Profile Fields:**
- Department
- Position Title
- Contact Number
- Address
- Photo ID

### Client
External clients and stakeholders who interact with the system.

### Pilot
Remote pilots with various certifications and operational responsibilities.

**Profile Fields:**
- Role: Chief Remote Pilot or Remote Pilot
- ARN (Aviation Reference Number)
- REPL Number and Expiry Date
- Medical Clearance Date
- Certifications
- Availability Status (Available, On Mission, Unavailable)
- Home Base Location
- Emergency Contact Information
- Contact Number and Address
- Photo ID
- Notes

## User Model

The project uses a custom `CustomUser` model that extends Django's `AbstractBaseUser` and `PermissionsMixin`.

**Key Features:**
- Email-based authentication (no username)
- Required fields: email, first_name, last_name, role
- Automatic timestamping (date_joined)
- Active/inactive status management
- Staff permissions

## Creating Users

### Via Admin Interface

1. Navigate to `http://localhost:8000/admin/`
2. Click on "Users" under the Accounts section
3. Click "Add User"
4. Fill in required fields:
   - Email
   - First Name
   - Last Name
   - Role
   - Password
5. Save the user

### Via Management Command

Create a superuser:
```bash
python manage.py createsuperuser
```

### Programmatically

```python
from accounts.models import CustomUser

# Create a regular user
user = CustomUser.objects.create_user(
    email='user@example.com',
    password='securepassword',
    first_name='John',
    last_name='Doe',
    role='staff'
)

# Create a superuser
admin = CustomUser.objects.create_superuser(
    email='admin@example.com',
    password='adminpassword',
    first_name='Admin',
    last_name='User'
)
```

## Profile Management

### Staff Profiles

Staff profiles are created and managed separately from the user account:

```python
from accounts.models import StaffProfile

staff_profile = StaffProfile.objects.create(
    user=user,
    department='Operations',
    position_title='Operations Manager',
    contact_number='+1234567890',
    address='123 Main St, City, Country'
)
```

### Pilot Profiles

Pilot profiles contain detailed certification and operational information:

```python
from accounts.models import PilotProfile

pilot_profile = PilotProfile.objects.create(
    user=user,
    role='remote_pilot',
    arn='ARN123456',
    repl_number='REPL789',
    contact_number='+1234567890',
    address='456 Aviation Way, City, Country',
    availability_status='available',
    home_base_location='Main Base'
)
```

## Operator Certificates

Manage REOC (Remotely Piloted Aircraft Operator Certificate) information:

```python
from accounts.models import OperatorCertificate

cert = OperatorCertificate.objects.create(
    reoc_number='REOC-2024-001',
    company_name='darklightMETA Studio',
    contact_email='operations@darklightmeta.com',
    issue_date='2024-01-01',
    expiry_date='2025-01-01'
)
```

## Authentication

Users authenticate using their email address and password:

```python
from django.contrib.auth import authenticate, login

user = authenticate(email='user@example.com', password='password')
if user is not None:
    login(request, user)
```

## Permissions and Groups

The custom user model integrates with Django's permission system:

- Superusers have all permissions
- Staff users can access the admin interface if `is_staff=True`
- Custom permissions can be added to models and assigned to users/groups

## Best Practices

1. Always use email for authentication
2. Enforce strong password policies
3. Regularly update medical clearances and certifications for pilots
4. Monitor certificate expiry dates
5. Keep emergency contact information up to date
6. Use photo IDs for identification verification
7. Maintain accurate availability status for pilots

## API Endpoints

See [API Documentation](api.md) for RESTful API endpoints related to user management.
