import os
from pathlib import Path
from django.test import TestCase
from django.conf import settings
from roster.models import Player, Team
from roster.services.player_import import PlayerImportService

class TestDataImportTestCase(TestCase):
    """Test importing the actual test_data.csv file."""

    def test_import_real_csv(self):
        """Verify that data/test_data.csv can be imported successfully."""
        # Locate the CSV file relative to the backend directory
        # Assuming backend is at project_root/backend
        # and data is at project_root/data
        base_dir = settings.BASE_DIR.parent  # This should be project_root
        csv_path = base_dir / "data" / "test_data.csv"

        if not csv_path.exists():
            # Fallback for different environment structures
            csv_path = Path("..") / "data" / "test_data.csv"
        
        if not csv_path.exists():
            self.fail(f"test_data.csv not found at {csv_path.resolve()}")

        print(f"Importing from {csv_path.resolve()}")
        
        result = PlayerImportService.import_from_csv(csv_path)
        
        self.assertGreater(result["processed"], 0, "Should process at least one row")
        self.assertGreater(result["created"], 0, "Should create at least one player")
        
        # Verify some data integrity if possible
        # e.g. check if a known player exists
        # Since I don't know the exact content, I'll just check counts
        self.assertTrue(Player.objects.exists())
        self.assertTrue(Team.objects.exists())
