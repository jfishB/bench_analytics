"""Test settings for backend."""  # pragma: no cover

from .settings import *  # noqa: F401, F403  # pragma: no cover

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
