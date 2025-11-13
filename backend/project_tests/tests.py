from django.test import SimpleTestCase


class ProjectSmokeTests(SimpleTestCase):
    def test_manage_py_discovery(self):
        # Simple assertion to ensure tests in the project_tests app are
        # discovered by the Django test runner when `manage.py test` is run
        self.assertTrue(True)
