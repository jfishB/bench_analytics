"""
django app configuration for simulator.
defines app name and default primary key field type.
automatically loaded by django when app is in INSTALLED_APPS.
"""

from django.apps import AppConfig


class SimulatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "simulator"
