from django.test import TestCase
from roster.models import Player, Team

class PlayerModelTests(TestCase):
    """Test Player model functionality."""

    def setUp(self):
        self.team = Team.objects.create(id=1)

    def test_create_player(self):
        """Test creating a player."""
        player = Player.objects.create(name="Test Player", team=self.team, home_run=10)
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.team, self.team)
        self.assertEqual(player.home_run, 10)

    def test_player_str(self):
        """Test player string representation."""
        player = Player.objects.create(name="John Doe", team=self.team)
        self.assertEqual(str(player), "John Doe")
