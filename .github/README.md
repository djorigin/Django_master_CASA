# GitHub Actions Documentation for Django CASA Project

## 🚀 GitHub Actions Setup Guide

This repository is configured with a comprehensive CI/CD pipeline using GitHub Actions. Here's what's included:

## 📋 Workflow Overview

### 1. **Main CI/CD Pipeline** (`django.yml`)
**Triggers:** Push to `main` or `feature/*` branches, Pull Requests to `main`

**Jobs:**
- **Test Job**: 
  - Runs on Python 3.11 & 3.12
  - Tests with both SQLite and PostgreSQL
  - Generates coverage reports
  - Uploads to Codecov
- **Lint Job**: Code quality checks (Black, isort, flake8, mypy)
- **Security Job**: Safety & Bandit security scans
- **Deploy Job**: Production deployment (when pushed to main)

### 2. **Code Quality Check** (`code-quality.yml`)
**Triggers:** Pull Requests to `main`

**Features:**
- Black code formatting verification
- Import sorting with isort
- PEP 8 compliance with flake8
- Type checking with mypy
- Automatic PR comments with results

### 3. **Security Scanning** (`security.yml`)
**Triggers:** Weekly schedule, Push to main, Pull Requests

**Security Checks:**
- Known vulnerability scanning with Safety
- Static analysis with Bandit
- Django deployment security checks
- Artifact upload for security reports

### 4. **Dependency Updates** (`dependency-update.yml`)
**Triggers:** Weekly schedule (Mondays), Manual trigger

**Features:**
- Automated dependency updates
- Conflict resolution
- Automatic Pull Request creation
- Change detection and reporting

## 🛠️ Setup Instructions

### Step 1: Enable GitHub Actions
1. Push the `.github/workflows/` directory to your repository
2. GitHub Actions will automatically detect and enable the workflows

### Step 2: Configure Repository Secrets
Add these secrets in your GitHub repository settings:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets for Deployment:**
- `DEPLOY_HOST`: Your production server IP/domain
- `DEPLOY_USER`: SSH username for deployment
- `DEPLOY_KEY`: SSH private key for deployment

**Optional Secrets:**
- `CODECOV_TOKEN`: For coverage reporting (get from codecov.io)

### Step 3: Repository Settings
1. **Branch Protection Rules** (recommended):
   ```
   Settings → Branches → Add rule
   Branch name pattern: main
   ✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   Select: django / test, django / lint, django / security
   ```

2. **Enable Discussions** (optional):
   ```
   Settings → General → Features → Discussions
   ```

## 📊 Monitoring & Reports

### Test Coverage
- Coverage reports are generated on every test run
- Uploaded to Codecov (if token configured)
- HTML reports available as workflow artifacts

### Security Reports
- Weekly security scans
- Reports uploaded as workflow artifacts
- Safety & Bandit analysis included

### Code Quality Metrics
- Automated code formatting checks
- Import organization verification
- PEP 8 compliance monitoring
- Type hint validation

## 🔄 Workflow Status Badges

Add these badges to your README.md:

```markdown
![Django CI](https://github.com/djorigin/Django_master_CASA/workflows/Django%20CI/CD%20Pipeline/badge.svg)
![Code Quality](https://github.com/djorigin/Django_master_CASA/workflows/Code%20Quality%20Check/badge.svg)
![Security](https://github.com/djorigin/Django_master_CASA/workflows/Security%20Scan/badge.svg)
```

## 🎯 Best Practices

### For Developers:
1. **Before Pushing:**
   ```bash
   # Format code
   black .
   isort .
   
   # Run tests locally
   python manage.py test --settings=darklightMETA_studio.test_settings
   
   # Check for issues
   flake8 .
   ```

2. **Branch Naming:**
   - Use `feature/description` for new features
   - Use `bugfix/description` for bug fixes
   - Use `hotfix/description` for urgent fixes

3. **Commit Messages:**
   ```
   feat: add new user authentication
   fix: resolve email validation issue
   docs: update API documentation
   test: add unit tests for user model
   refactor: optimize database queries
   ```

### For Project Maintenance:
- Review dependency update PRs weekly
- Monitor security scan results
- Keep workflows updated with latest actions
- Review and update branch protection rules

## 🚀 Deployment Options

The deployment job is currently a placeholder. Configure it based on your deployment method:

### Option 1: SSH Deployment
```yaml
- name: Deploy via SSH
  run: |
    echo "${{ secrets.DEPLOY_KEY }}" > deploy_key
    chmod 600 deploy_key
    ssh -i deploy_key -o StrictHostKeyChecking=no ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} "
      cd /path/to/your/app &&
      git pull origin main &&
      pip install -r requirements.txt &&
      python manage.py migrate &&
      python manage.py collectstatic --noinput &&
      sudo systemctl restart gunicorn
    "
```

### Option 2: Docker Deployment
```yaml
- name: Build and push Docker image
  run: |
    docker build -t djorigin/casa-app:latest .
    docker push djorigin/casa-app:latest
```

### Option 3: Cloud Platform (AWS/Azure/GCP)
- Configure specific deployment actions for your cloud provider
- Use their official GitHub Actions

## ✅ Getting Started Checklist

- [ ] Push `.github/workflows/` to your repository
- [ ] Configure repository secrets for deployment
- [ ] Set up branch protection rules
- [ ] Add workflow status badges to README
- [ ] Configure Codecov (optional)
- [ ] Test the workflows with a pull request
- [ ] Customize deployment method
- [ ] Review and adjust security settings

Your Django CASA project is now equipped with professional CI/CD automation! 🎉