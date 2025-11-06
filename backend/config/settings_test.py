from . import settings

# Use an in-memory SQLite database for tests to avoid requiring Postgres locally.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
