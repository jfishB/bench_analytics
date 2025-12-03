import os  # pragma: no cover

import django  # pragma: no cover
from django.conf import settings  # pragma: no cover

# Configure Django settings for all pytest runs.  # pragma: no cover
# locally it uses sql lite and in CI it uses the test data base settings  # pragma: no cover
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")  # pragma: no cover


def pytest_configure():  # pragma: no cover
    """Configure Django for pytest."""  # pragma: no cover
    if not settings.configured:  # pragma: no cover
        django.setup()  # pragma: no cover
