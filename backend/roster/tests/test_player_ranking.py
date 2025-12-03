from django.test import TestCase

from roster.models import Player, Team
from roster.services.player_ranking import (
    create_player_with_stats,
    get_ranked_players,
    get_team_by_id,
    update_player_stats,
)


class PlayerRankingServiceTestCase(TestCase):
    """Test PlayerRankingService and helper functions."""

    def setUp(self):
        self.team = Team.objects.create(id=1)
        # Create players with different stats
        self.p1 = Player.objects.create(name="Player 1", team=self.team, bb_percent=10.0, pa=100)
        self.p2 = Player.objects.create(name="Player 2", team=self.team, bb_percent=5.0, pa=100)
        self.p3 = Player.objects.create(name="Player 3", team=self.team, bb_percent=15.0, pa=100)

    def test_get_ranked_players(self):
        """Test fetching ranked players (placeholder logic)."""
        # The current placeholder implementation just returns players with wos_score=0
        # We verify it returns the correct structure
        ranked = get_ranked_players()
        self.assertEqual(len(ranked), 3)
        self.assertIn("wos_score", ranked[0])
        self.assertEqual(ranked[0]["wos_score"], 0.0)

    def test_get_ranked_players_top_n(self):
        """Test fetching ranked players with top_n limit."""
        ranked = get_ranked_players(top_n=2)
        self.assertEqual(len(ranked), 2)

    def test_create_player_with_stats(self):
        """Test helper to create player."""
        p = create_player_with_stats("New Guy", bb_percent=12.5, team=self.team)
        self.assertEqual(p.name, "New Guy")
        self.assertEqual(p.bb_percent, 12.5)
        self.assertEqual(p.team, self.team)

    def test_update_player_stats(self):
        """Test helper to update player."""
        p = update_player_stats(self.p1.id, bb_percent=20.0)
        
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.bb_percent, 20.0)

    def test_get_team_by_id(self):
        """Test helper to get team."""
        t = get_team_by_id(self.team.id)
        self.assertEqual(t, self.team)

        t_none = get_team_by_id(999)
        self.assertIsNone(t_none)

    def test_get_ranked_players_empty(self):
        """Test ranking with no players."""
        # Clear players created in setUp
        Player.objects.all().delete()
        result = get_ranked_players()
        self.assertEqual(result, [])
