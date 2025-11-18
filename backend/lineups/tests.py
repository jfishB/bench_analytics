from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


class LineupViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create team and players
        # teams; the model no longer accepts it. Be defensive so tests work
        # across both schema versions.
        self.team = Team.objects.create()
        self.players = []
        for i in range(1, 10):
            p = Player.objects.create(name=f"Player {i}", team=self.team)
            self.players.append(p)

        # Users
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")

        self.base_url = "/api/v1/lineups/"

    def test_post_valid_returns_201(self):
        # Test algorithm-only mode: POST only team_id, get suggested lineup without saving
        payload = {"team_id": self.team.id}

        # Authenticate as creator and POST only the team_id
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        # Algorithm mode doesn't save to DB, so no 'id' field
        self.assertIn("team_id", resp.data)
        self.assertIn("players", resp.data)
        self.assertEqual(len(resp.data["players"]), 9)
        # Verify each player has required fields
        for player in resp.data["players"]:
            self.assertIn("player_id", player)
            self.assertIn("player_name", player)
            self.assertIn("position", player)
            self.assertIn("batting_order", player)

    def test_post_manual_save_returns_201(self):
        # Test manual save mode: POST with players and batting orders, saves to DB
        payload = {
            "team_id": self.team.id,
            "name": "Manual Lineup",
            "players": [
                {
                    "player_id": self.players[i].id,
                    "position": "1B",
                    "batting_order": i + 1,
                }
                for i in range(9)
            ],
        }

        # Authenticate as creator and POST full lineup
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        # Manual save mode saves to DB, so 'id' field should be present
        self.assertIn("id", resp.data)
        self.assertIn("team_id", resp.data)
        self.assertIn("name", resp.data)
        self.assertIn("players", resp.data)
        self.assertEqual(resp.data["name"], "Manual Lineup")
        self.assertEqual(len(resp.data["players"]), 9)
        # Verify lineup was saved to database
        lineup = Lineup.objects.get(id=resp.data["id"])
        self.assertEqual(lineup.name, "Manual Lineup")
        self.assertEqual(lineup.team_id, self.team.id)
        self.assertEqual(lineup.players.count(), 9)

    def test_get_detail_returns_200(self):
        lineup = Lineup.objects.create(
            team=self.team,
            created_by=self.creator,
        )
        LineupPlayer.objects.create(lineup=lineup, player=self.players[0], position="P", batting_order="1")

        url = f"{self.base_url}{lineup.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], lineup.id)

    def test_delete_only_creator_or_superuser(self):
        lineup = Lineup.objects.create(
            team=self.team,
            created_by=self.creator,
        )

        url = f"{self.base_url}{lineup.id}/"

        # unauthenticated -> 403
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 403)

        # other user -> 403
        self.client.force_authenticate(user=self.other)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 403)

        # creator -> 204
        self.client.force_authenticate(user=self.creator)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

    def test_superuser_can_delete(self):
        lineup = Lineup.objects.create(
            team=self.team,
            created_by=self.creator,
        )
        url = f"{self.base_url}{lineup.id}/"
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)


# Example usage or ad-hoc testing should be run in a script or Django shell,
# not at module import time. Keep tests module import-safe so the test
# discovery/import process doesn't execute side-effectful code.
