import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from roster.models import Player, Team
from roster.services.player_import import PlayerImportService


class PlayerImportServiceTestCase(TestCase):
    """Test PlayerImportService functionality."""

    def setUp(self):
        self.team = Team.objects.create(id=1)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "test_players.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_csv(self, rows):
        """Helper to create a CSV file with given rows."""
        with open(self.csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return str(self.csv_path)

    def test_import_from_csv_success(self):
        """Test successful import of valid player data."""
        rows = [
            {
                "last_name, first_name": "Judge, Aaron",
                "player_id": "12345",
                "year": "2024",
                "pa": "600",
                "hit": "150",
                "home_run": "50",
                "team_id": str(self.team.id),
            },
            {
                "last_name, first_name": "Soto, Juan",
                "player_id": "67890",
                "year": "2024",
                "pa": "650",
                "hit": "160",
                "home_run": "40",
                # No team_id, should use global or None
            },
        ]
        self.create_csv(rows)

        result = PlayerImportService.import_from_csv(self.csv_path, team_id=self.team.id)

        self.assertEqual(result["created"], 2)
        self.assertEqual(Player.objects.count(), 2)

        judge = Player.objects.get(savant_player_id=12345)
        self.assertEqual(judge.name, "Judge, Aaron")
        self.assertEqual(judge.home_run, 50)
        self.assertEqual(judge.team, self.team)

        soto = Player.objects.get(savant_player_id=67890)
        self.assertEqual(soto.name, "Soto, Juan")
        self.assertEqual(soto.team, self.team)  # Fallback to global team

    def test_import_updates_existing_player(self):
        """Test that importing updates existing players instead of creating duplicates."""
        # Create initial player
        Player.objects.create(
            name="Judge, Aaron",
            savant_player_id=12345,
            team=self.team,
            home_run=10
        )

        rows = [
            {
                "last_name, first_name": "Judge, Aaron",
                "player_id": "12345",
                "year": "2024",
                "pa": "600",
                "hit": "150",
                "home_run": "62",  # Updated value
                "team_id": str(self.team.id),
            }
        ]
        self.create_csv(rows)

        result = PlayerImportService.import_from_csv(self.csv_path)

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(Player.objects.count(), 1)

        judge = Player.objects.get(name="Judge, Aaron")
        self.assertEqual(judge.home_run, 62)

    def test_import_dry_run(self):
        """Test dry run mode does not save changes."""
        rows = [
            {
                "last_name, first_name": "New Player",
                "player_id": "99999",
                "year": "2024",
                "pa": "100",
            }
        ]
        self.create_csv(rows)

        result = PlayerImportService.import_from_csv(self.csv_path, dry_run=True)

        self.assertEqual(result["processed"], 1)
        self.assertEqual(Player.objects.count(), 0)  # Nothing saved

    def test_file_not_found(self):
        """Test error when file does not exist."""
        with self.assertRaises(FileNotFoundError):
            PlayerImportService.import_from_csv("non_existent.csv")

    def test_empty_file(self):
        """Test importing an empty file."""
        # Create empty file
        with open(self.csv_path, "w") as f:
            pass

        # Should fail or return empty result depending on implementation
        # The current implementation catches Exception on DictReader if empty?
        # Actually DictReader on empty file yields no rows.
        result = PlayerImportService.import_from_csv(self.csv_path)
        self.assertEqual(result["processed"], 0)

    def test_name_parsing_formats(self):
        """Test various name formats."""
        rows = [
            {"last_name, first_name": "Doe, John", "player_id": "1"},
            {"name": "Smith, Jane", "player_id": "2"},
            {"first_name": "Bob", "last_name": "Jones", "player_id": "3"},
        ]
        # We need to write a header that includes all possible keys to avoid DictReader mismatch if we want strictness,
        # but DictReader just reads what's there.
        # Let's write them carefully.
        with open(self.csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["last_name, first_name", "name", "first_name", "last_name", "player_id", "year", "pa"])
            writer.writeheader()
            writer.writerows(rows)

        result = PlayerImportService.import_from_csv(self.csv_path)
        self.assertEqual(result["created"], 3)

        self.assertTrue(Player.objects.filter(name="Doe, John").exists())
        self.assertTrue(Player.objects.filter(name="Smith, Jane").exists())
        self.assertTrue(Player.objects.filter(name="Jones, Bob").exists())

    def test_data_conversion_robustness(self):
        """Test that invalid numbers are handled gracefully (converted to None or 0)."""
        rows = [
            {
                "last_name, first_name": "Robusto",
                "player_id": "100",
                "pa": "invalid",  # Should be None
                "hit": "10%",     # Should strip %
                "bb_percent": "12.5",
            }
        ]
        self.create_csv(rows)

        PlayerImportService.import_from_csv(self.csv_path)
        player = Player.objects.get(name="Robusto")

        self.assertIsNone(player.pa)
        self.assertEqual(player.hit, 10)
        self.assertEqual(player.bb_percent, 12.5)
