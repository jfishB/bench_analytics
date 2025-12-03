"""Test settings for backend."""  # pragma: no cover

from .settings import *  # noqa: F401, F403  # pragma: no cover

DATABASES = {  # pragma: no cover
    "default": {  # pragma: no cover
        "ENGINE": "django.db.backends.sqlite3",  # pragma: no cover
        "NAME": ":memory:",  # pragma: no cover
    }  # pragma: no cover
}  # pragma: no cover
