from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


class LineupViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create team and players
        self.team = Team.objects.create(name="Tigers")
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

    @patch("lineups.views.algorithm_create_lineup")
    def test_post_valid_returns_201(self, mock_algorithm):
        # Prepare payload
        payload = {
            "team_id": self.team.id,
            "name": "My Lineup",
            "opponent_pitcher_id": self.players[0].id,
            "players": [
                {"player_id": p.id, "position": "1B"} for p in self.players[:9]
            ],
        }

        # Prepare a lineup object that algorithm would return
        lineup = Lineup.objects.create(
            team=self.team,
            name="My Lineup",
            opponent_pitcher_id=self.players[0].id,
            created_by=self.creator,
        )
        for idx, p in enumerate(self.players[:9], start=1):
            LineupPlayer.objects.create(
                lineup=lineup, player=p, position="1B", batting_order=idx
            )

        mock_algorithm.return_value = lineup

        # Authenticate as creator
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data["name"], "My Lineup")

    def test_get_detail_returns_200(self):
        lineup = Lineup.objects.create(
            team=self.team,
            name="Saved",
            opponent_pitcher_id=self.players[0].id,
            created_by=self.creator,
        )
        LineupPlayer.objects.create(
            lineup=lineup, player=self.players[0], position="P", batting_order=1
        )

        url = f"{self.base_url}{lineup.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], lineup.id)
        self.assertEqual(resp.data["name"], "Saved")

    def test_delete_only_creator_or_superuser(self):
        lineup = Lineup.objects.create(
            team=self.team,
            name="Deletable",
            opponent_pitcher_id=self.players[0].id,
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
            name="ByAdmin",
            opponent_pitcher_id=self.players[0].id,
            created_by=self.creator,
        )
        url = f"{self.base_url}{lineup.id}/"
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

    @patch("lineups.views.algorithm_create_lineup")
    def test_post_without_opponent_pitcher_succeeds(self, mock_algorithm):
        """Test creating a lineup without opponent_pitcher (new optional field)."""
        # Payload without opponent_pitcher_id
        payload = {
            "team_id": self.team.id,
            "name": "No Opponent Lineup",
            "players": [
                {"player_id": p.id, "position": "1B"} for p in self.players[:9]
            ],
        }

        # Create lineup without opponent_pitcher
        lineup = Lineup.objects.create(
            team=self.team,
            name="No Opponent Lineup",
            opponent_pitcher=None,
            created_by=self.creator,
        )
        for idx, p in enumerate(self.players[:9], start=1):
            LineupPlayer.objects.create(
                lineup=lineup, player=p, position="1B", batting_order=idx
            )

        mock_algorithm.return_value = lineup

        # Authenticate and make request
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")

        # Verify response
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data["name"], "No Opponent Lineup")
        self.assertIsNone(resp.data.get("opponent_pitcher_id"))
