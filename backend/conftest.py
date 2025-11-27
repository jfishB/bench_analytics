import os

import django
from django.conf import settings

# Configure Django settings for all pytest runs (uses SQLite instead of PostgreSQL)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")


def pytest_configure():
    """Configure Django for pytest."""
    if not settings.configured:
        django.setup()
