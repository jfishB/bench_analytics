import json

from django.test import TestCase

from django.contrib.auth import get_user_model

from roster.models import Team, Player
from lineups.models import Lineup, LineupPlayer


class LineupIntegrationTests(TestCase):
    """Integration tests to ensure lineup components (view, handler, algorithm, persistence)
    can communicate end-to-end.
    """

    def setUp(self):
        # Create a team and 9 players with minimal stats required by the algorithm
        self.team = Team.objects.create()

        # Create 9 players with non-zero b_game/pa so algorithm metrics are calculable
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)

        # Create a user to act as the creator when saving lineups
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass")

    def test_generate_suggested_lineup_endpoint(self):
        """POST /api/v1/lineups/ with team_id should return a suggested lineup in expected shape."""

        url = "/api/v1/lineups/"
        payload = {"team_id": self.team.id}

        resp = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertIn("team_id", data)
        self.assertEqual(data["team_id"], self.team.id)
        self.assertIn("players", data)
        self.assertIsInstance(data["players"], list)

        players = data["players"]
        # The algorithm should return up to 9 players
        self.assertGreaterEqual(len(players), 1)
        self.assertLessEqual(len(players), 9)

        # Ensure each suggested player has required fields and unique batting orders
        orders = set()
        for p in players:
            self.assertIn("player_id", p)
            self.assertIn("player_name", p)
            self.assertIn("batting_order", p)
            orders.add(p["batting_order"])

        self.assertEqual(len(orders), len(players))

    def test_save_lineup_end_to_end(self):
        """POST /api/v1/lineups/ with full players + batting orders should persist a Lineup."""

        url = "/api/v1/lineups/"

        payload = {
            "team_id": self.team.id,
            "name": "Test Save",
            "players": [
                {"player_id": p.id, "batting_order": idx + 1} for idx, p in enumerate(self.players)
            ],
        }

        # Authenticate as a user so created_by is set
        self.client.force_login(self.user)

        resp = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertIn("id", data)
        lineup_id = data["id"]

        # Verify lineup persisted in DB
        lineup = Lineup.objects.filter(pk=lineup_id).first()
        self.assertIsNotNone(lineup)
        self.assertEqual(lineup.team_id, self.team.id)
        self.assertEqual(lineup.name, "Test Save")
        self.assertEqual(lineup.created_by_id, self.user.id)

        # Verify LineupPlayers
        lp_qs = LineupPlayer.objects.filter(lineup=lineup).order_by("batting_order")
        self.assertEqual(lp_qs.count(), 9)
        for idx, lp in enumerate(lp_qs):
            self.assertEqual(lp.batting_order, idx + 1)
            self.assertEqual(lp.player.team_id, self.team.id)
