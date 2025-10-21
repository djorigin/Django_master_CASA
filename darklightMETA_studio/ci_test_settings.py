"""
CI/CD Test Settings for GitHub Actions
====================================

This file contains settings optimized for continuous integration testing.
It uses SQLite in-memory database for speed and disables unnecessary features.
"""

from .settings import *

# Override database to use SQLite in memory for faster testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "init_command": "PRAGMA foreign_keys=ON;",
        },
    }
}

# Disable migrations for faster testing
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable logging during tests
LOGGING_CONFIG = None

# Use console email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable timezone warnings
USE_TZ = True

# Debug should be False in tests
DEBUG = False

# Secret key for testing
SECRET_KEY = "test-secret-key-for-ci-cd-only-not-for-production"

# Disable CSRF for API testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Media and static files for testing
MEDIA_ROOT = "/tmp/test_media"
STATIC_ROOT = "/tmp/test_static"

# Test-specific apps (if needed)
# INSTALLED_APPS += ['django_coverage']