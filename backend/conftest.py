import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure():
    """Configure Django for pytest."""
    if not settings.configured:
        django.setup()
