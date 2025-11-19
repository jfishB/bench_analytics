from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


class LineupIntegrationTests(TestCase):
    """Integration tests that exercise the view -> algorithm path end-to-end.

    These tests avoid mocking the algorithm or validator and test:
    1. Algorithm-only mode: POST team_id returns suggested lineup without saving
    2. Manual save mode: POST with full lineup data saves to database
    """

    def setUp(self):
        self.client = APIClient()
        # create team and 9 players
        self.team = Team.objects.create()
        self.players = []
        for i in range(1, 10):
            p = Player.objects.create(name=f"Player {i}", team=self.team)
            self.players.append(p)

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.client.force_authenticate(user=self.creator)
        self.base_url = "/api/v1/lineups/"

    def test_post_team_id_returns_suggested_lineup(self):
        """Test algorithm mode: POST team_id returns suggested lineup WITHOUT saving to DB."""
        initial_lineup_count = Lineup.objects.count()
        payload = {"team_id": self.team.id}
        resp = self.client.post(self.base_url, payload, format="json")

        # Expect 201 Created
        self.assertEqual(resp.status_code, 201)
        # Algorithm mode doesn't save, so no 'id' field
        self.assertNotIn("id", resp.data)
        self.assertIn("team_id", resp.data)
        self.assertIn("players", resp.data)
        self.assertEqual(len(resp.data["players"]), 9)

        # Verify lineup was NOT saved to database
        self.assertEqual(Lineup.objects.count(), initial_lineup_count)

        # Verify batting orders are consecutive 1-9
        batting_orders = [p["batting_order"] for p in resp.data["players"]]
        self.assertEqual(sorted(batting_orders), list(range(1, 10)))

    def test_post_full_payload_saves_lineup(self):
        """Test manual save mode: POST with full lineup data saves to database."""
        payload = {
            "team_id": self.team.id,
            "name": "Integration Test Lineup",
            "players": [{"player_id": self.players[i].id, "position": "1B", "batting_order": i + 1} for i in range(9)],
        }
        resp = self.client.post(self.base_url, payload, format="json")

        # Expect 201 Created
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)

        lineup_id = resp.data["id"]
        lineup = Lineup.objects.get(pk=lineup_id)

        # Check creator and team
        self.assertEqual(lineup.created_by_id, self.creator.id)
        self.assertEqual(lineup.team_id, self.team.id)
        self.assertEqual(lineup.name, "Integration Test Lineup")

        # Fetch persisted players and ensure 9 entries with consecutive batting orders
        lp_qs = LineupPlayer.objects.filter(lineup=lineup).order_by("batting_order")
        self.assertEqual(lp_qs.count(), 9)
        batting_orders = [lp.batting_order for lp in lp_qs]
        self.assertEqual(batting_orders, list(range(1, 10)))
