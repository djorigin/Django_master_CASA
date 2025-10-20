# CASA Master Project

This is the Django Master CASA (Civil Aviation Safety Authority) project for managing aviation personnel and operations.

## Project Overview

The CASA Master Project is a Django-based web application designed to manage:
- Staff profiles and accounts
- Pilot profiles with certifications and credentials
- Operator certificates (REOC - Remotely Piloted Aircraft Operator Certificate)
- User authentication with role-based access control

## Features

- Custom user model with email-based authentication
- Role-based access (Staff, Client, Pilot)
- Staff profile management with department and position tracking
- Pilot profile management with:
  - ARN (Aviation Reference Number)
  - REPL (Remote Pilot License) tracking
  - Medical clearance monitoring
  - Availability status management
  - Emergency contact information
- Operator certificate management with expiry tracking
- Django REST Framework integration

## Technology Stack

- Django 5.2.7
- PostgreSQL database
- Django REST Framework
- Python 3.x

## Project Structure

```
Django_master_CASA/
├── accounts/              # User and profile management app
│   ├── models.py         # CustomUser, StaffProfile, PilotProfile, OperatorCertificate
│   ├── admin.py          # Admin interface configurations
│   └── views.py          # API views
├── darklightMETA_studio/ # Main project settings
│   ├── settings.py       # Project configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
└── manage.py             # Django management script
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/djorigin/Django_master_CASA.git
cd Django_master_CASA
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the database:
   - Update database settings in `darklightMETA_studio/settings.py`
   - Ensure PostgreSQL is running and accessible

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Database Configuration

The project uses PostgreSQL. Update the following in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_password',
        'HOST': 'your_host',
        'PORT': '5432',
    }
}
```

### Allowed Hosts

Configure `ALLOWED_HOSTS` in `settings.py` for your deployment environment.

## User Roles

The application supports three user roles:
- **Staff**: Administrative and operational staff members
- **Client**: External clients and stakeholders
- **Pilot**: Remote pilots with varying levels of certification

## Models

### CustomUser
Custom user model with email-based authentication and role assignment.

### StaffProfile
Extended profile for staff members with department and contact information.

### PilotProfile
Detailed profile for pilots including:
- Certification tracking (ARN, REPL)
- Medical clearance
- Availability status
- Emergency contacts

### OperatorCertificate
Manages REOC (Remotely Piloted Aircraft Operator Certificate) information.

## Contributing

This is a private project for darklightMETA studio operations.

## License

Proprietary - All rights reserved

## Contact

For questions or support, please contact the darklightMETA studio development team.

## Repository

This project is maintained at: [https://github.com/djorigin/Django_master_CASA](https://github.com/djorigin/Django_master_CASA)
