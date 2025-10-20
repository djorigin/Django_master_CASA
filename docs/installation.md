# Installation Guide

## Prerequisites

Before installing the CASA Master Project, ensure you have:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- virtualenv or venv

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/djorigin/Django_master_CASA.git
cd Django_master_CASA
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and update the following:
- `DB_NAME`: Your PostgreSQL database name
- `DB_USER`: Your database user
- `DB_PASSWORD`: Your database password
- `DB_HOST`: Database host (usually localhost)
- `SECRET_KEY`: Generate a new secret key

To generate a secret key:
```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Set Up Database

Create a PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE darklightmeta;
CREATE USER dev_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE darklightmeta TO dev_admin;
\q
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

The application should now be running at `http://localhost:8000/`

## Accessing the Admin Interface

Navigate to `http://localhost:8000/admin/` and log in with the superuser credentials you created.

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `systemctl status postgresql`
- Check database credentials in settings
- Ensure database user has proper permissions

### Import Errors

- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Static Files Not Loading

- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL` settings

## Next Steps

- Review [User Management](user-management.md) documentation
- Explore the [API Documentation](api.md)
- Configure [Deployment](deployment.md) settings for production
