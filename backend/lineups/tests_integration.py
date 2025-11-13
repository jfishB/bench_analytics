from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


class LineupIntegrationTests(TestCase):
    """Integration tests that exercise the view -> algorithm path end-to-end.

    These tests avoid mocking the algorithm or validator and assert the
    algorithm runs when the view is called with a `team_id` and that the
    persisted Lineup + LineupPlayer rows are created with valid batting
    orders and creator information.
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

    def test_post_team_id_creates_lineup_and_players(self):
        payload = {"team_id": self.team.id}
        resp = self.client.post(self.base_url, payload, format="json")
        # Expect created
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)

        lineup_id = resp.data["id"]
        lineup = Lineup.objects.get(pk=lineup_id)
        # Check creator and team
        self.assertEqual(lineup.created_by_id, self.creator.id)
        self.assertEqual(lineup.team_id, self.team.id)

        # Fetch persisted players and ensure 9 entries with consecutive batting orders
        lp_qs = LineupPlayer.objects.filter(lineup=lineup).order_by("batting_order")
        self.assertEqual(lp_qs.count(), 9)
        batting_orders = [lp.batting_order for lp in lp_qs]
        self.assertEqual(batting_orders, list(range(1, 10)))
