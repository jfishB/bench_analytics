from django.test import TestCase
from lineups.services.algorithm_logic import algorithm_create_lineup
from lineups.services.input_data import CreateLineupInput, LineupPlayerInput
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

    @patch("lineups.views.validate_data")
    @patch("lineups.views.validate_lineup_model")
    @patch("lineups.views.algorithm_create_lineup")
    def test_post_valid_returns_201(self, mock_algorithm, mock_validate, mock_validate_data):
        # The view expects the frontend to send only a team_id. The view
        # will load players server-side and pass a CreateLineupInput to the
        # algorithm. Patch the algorithm to return (lineup, lineup_players)
        # as the real implementation does.
        payload = {"team_id": self.team.id}

        # Prepare a persisted lineup and its LineupPlayer rows to return
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator, name="Test")
        lineup_players = []
        for idx, p in enumerate(self.players[:9], start=1):
            lp = LineupPlayer.objects.create(lineup=lineup, player=p, position="1B", batting_order=idx)
            lineup_players.append(lp)

        mock_algorithm.return_value = (lineup, lineup_players)
        # Mock validate_data to return the validated payload structure the
        # algorithm expects. This avoids the view hitting domain validation
        # that we don't want exercised in this unit test.
        mock_validate_data.return_value = {
            "team": self.team,
            "players": self.players[:9],
            "created_by_id": self.creator.id,
        }
        # The view calls validate_lineup_model(lineup) after the algorithm
        # returns; patch it to True so this unit test focuses on the
        # view/algorithm contract rather than re-running domain validation.
        mock_validate.return_value = True

        # Authenticate as creator and POST only the team_id
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)

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