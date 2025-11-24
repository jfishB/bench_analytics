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

    def test_post_manual_save_returns_201(self):
        # Test manual save mode: POST with players and batting orders, saves to DB
        payload = {
            "team_id": self.team.id,
            "name": "Manual Lineup",
            "players": [
                {
                    "player_id": self.players[i].id,
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

    def test_delete_only_creator_or_superuser(self):
        lineup = Lineup.objects.create(
            team=self.team,
            created_by=self.creator,
        )

        url = f"{self.base_url}{lineup.id}/"

        # unauthenticated -> 401
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 401)

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

    def test_viewset_list_returns_only_user_lineups(self):
        """Test that /api/v1/lineups/saved/ only returns lineups created by the authenticated user."""
        # Create lineups for different users
        lineup1 = Lineup.objects.create(
            team=self.team,
            name="Creator's Lineup 1",
            created_by=self.creator,
        )
        lineup2 = Lineup.objects.create(
            team=self.team,
            name="Creator's Lineup 2",
            created_by=self.creator,
        )
        lineup3 = Lineup.objects.create(
            team=self.team,
            name="Other's Lineup",
            created_by=self.other,
        )

        # Authenticate as creator
        self.client.force_authenticate(user=self.creator)
        resp = self.client.get(f"{self.base_url}saved/")
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        lineup_ids = [item["id"] for item in data]
        
        # Should only see own lineups
        self.assertIn(lineup1.id, lineup_ids)
        self.assertIn(lineup2.id, lineup_ids)
        self.assertNotIn(lineup3.id, lineup_ids)

    def test_viewset_superuser_sees_all_lineups(self):
        """Test that superusers can see all lineups via /api/v1/lineups/saved/."""
        lineup1 = Lineup.objects.create(
            team=self.team,
            name="Creator's Lineup",
            created_by=self.creator,
        )
        lineup2 = Lineup.objects.create(
            team=self.team,
            name="Other's Lineup",
            created_by=self.other,
        )

        # Authenticate as superuser
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get(f"{self.base_url}saved/")
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        lineup_ids = [item["id"] for item in data]
        
        # Should see all lineups
        self.assertIn(lineup1.id, lineup_ids)
        self.assertIn(lineup2.id, lineup_ids)

    def test_viewset_write_operations_disabled(self):
        """Test that POST, PUT, PATCH, DELETE are disabled on /api/v1/lineups/saved/."""
        self.client.force_authenticate(user=self.creator)
        
        # Create a lineup directly in DB to test update/delete
        lineup = Lineup.objects.create(
            team=self.team,
            name="Test Lineup",
            created_by=self.creator,
        )

        # Test POST (create) - should return 405 Method Not Allowed
        payload = {
            "team_id": self.team.id,
            "name": "New Lineup",
        }
        resp = self.client.post(f"{self.base_url}saved/", payload, format="json")
        self.assertEqual(resp.status_code, 405)

        # Test PUT (update) - should return 405 Method Not Allowed
        update_payload = {
            "team_id": self.team.id,
            "name": "Updated Lineup",
        }
        resp = self.client.put(f"{self.base_url}saved/{lineup.id}/", update_payload, format="json")
        self.assertEqual(resp.status_code, 405)

        # Test PATCH (partial update) - should return 405 Method Not Allowed
        patch_payload = {"name": "Patched Lineup"}
        resp = self.client.patch(f"{self.base_url}saved/{lineup.id}/", patch_payload, format="json")
        self.assertEqual(resp.status_code, 405)

        # Test DELETE - should return 405 Method Not Allowed
        resp = self.client.delete(f"{self.base_url}saved/{lineup.id}/")
        self.assertEqual(resp.status_code, 405)


# Example usage or ad-hoc testing should be run in a script or Django shell,
# not at module import time. Keep tests module import-safe so the test
# discovery/import process doesn't execute side-effectful code.
