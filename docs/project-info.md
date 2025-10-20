# Project Information

## CASA Master Project

**Official Repository**: [djorigin/Django_master_CASA](https://github.com/djorigin/Django_master_CASA)

### Project Identity

- **Name**: CASA Master Project
- **Owner**: djorigin
- **Repository**: Django_master_CASA
- **Type**: Django Web Application
- **Purpose**: Aviation Personnel and Operations Management

### Technology Stack

- **Framework**: Django 5.2.7
- **Language**: Python 3.x
- **Database**: PostgreSQL
- **API**: Django REST Framework

### Key Components

1. **Custom User Management**
   - Email-based authentication
   - Role-based access control (Staff, Client, Pilot)
   - Extended user profiles

2. **Pilot Management**
   - Certification tracking (ARN, REPL)
   - Medical clearance monitoring
   - Availability status management
   - Emergency contacts

3. **Staff Management**
   - Department and position tracking
   - Contact information
   - Photo identification

4. **Operator Certificates**
   - REOC management
   - Expiry date tracking

### Documentation

- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](installation.md) - Detailed setup instructions
- [User Management](user-management.md) - User and profile management
- [Contributing Guidelines](../CONTRIBUTING.md) - Development workflow

### Links

- **GitHub Repository**: https://github.com/djorigin/Django_master_CASA
- **Clone URL**: `git clone https://github.com/djorigin/Django_master_CASA.git`

### Quick Start

```bash
# Clone the repository
git clone https://github.com/djorigin/Django_master_CASA.git
cd Django_master_CASA

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Maintenance

This project is actively maintained by the darklightMETA studio development team.

For issues, questions, or contributions, please refer to the GitHub repository.

---

**Last Updated**: 2025-10-20  
**Repository**: djorigin/Django_master_CASA
