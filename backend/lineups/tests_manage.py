from django.test import SimpleTestCase
from django.conf import settings


class LineupsManageTests(SimpleTestCase):
    """Simple smoke tests for Django test discovery.

    These tests do not require database access and ensure that the
    Django test runner (`manage.py test`) discovers tests inside the
    `lineups` app.
    """

    def test_lineups_app_in_installed_apps(self):
        self.assertIn("lineups", settings.INSTALLED_APPS)

