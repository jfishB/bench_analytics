from django.apps import AppConfig


class ProjectTestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project_tests"
    verbose_name = "Project-level tests"
