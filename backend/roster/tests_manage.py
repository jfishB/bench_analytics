from django.conf import settings
from django.test import SimpleTestCase


class RosterManageTests(SimpleTestCase):
    """Simple smoke tests for Django test discovery in the roster app.

    These tests are intentionally lightweight (no DB) so they run fast
    and confirm that `manage.py test` picks up app tests.
    """

    def test_roster_app_in_installed_apps(self):
        self.assertIn("roster", settings.INSTALLED_APPS)
