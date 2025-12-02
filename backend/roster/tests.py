from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Player, Team
from .services.player_ranking import get_ranked_players


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


class PlayerRankingServiceTests(TestCase):
    """Test player ranking service functions."""

    def test_get_ranked_players_empty(self):
        """Test ranking with no players."""
        result = get_ranked_players()
        self.assertEqual(result, [])


class PlayerAPITests(APITestCase):
    """Test Player API endpoints."""

    def setUp(self):
        self.team = Team.objects.create(id=1)
        self.player = Player.objects.create(
            name="Aaron Judge",
            team=self.team,
            xwoba=0.476,
            bb_percent=18.3,
            barrel_batted_rate=24.7,
            k_percent=23.6,
        )

    def test_list_players(self):
        """Test GET /players/"""
        url = reverse("roster:player-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_player(self):
        """Test POST /players/"""
        url = reverse("roster:player-list")
        data = {"name": "Juan Soto", "team": self.team.id, "home_run": 40}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.count(), 2)

    def test_retrieve_player(self):
        """Test GET /players/{id}/"""
        url = reverse("roster:player-detail", kwargs={"pk": self.player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Aaron Judge")

    def test_update_player(self):
        """Test PATCH /players/{id}/"""
        url = reverse("roster:player-detail", kwargs={"pk": self.player.id})
        data = {"home_run": 62}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.home_run, 62)

    def test_delete_player(self):
        """Test DELETE /players/{id}/"""
        url = reverse("roster:player-detail", kwargs={"pk": self.player.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Player.objects.count(), 0)

    def test_ranked_players(self):
        """Test GET /players/ranked/"""
        url = reverse("roster:player-ranked")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("players", response.data)
        self.assertEqual(len(response.data["players"]), 1)
        self.assertIn("wos_score", response.data["players"][0])


class TeamAPITests(APITestCase):
    """Test Team API endpoints."""

    def test_list_teams(self):
        """Test GET /teams/"""
        Team.objects.create(id=1)
        url = reverse("roster:team-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_team(self):
        """Test POST /teams/"""
        url = reverse("roster:team-list")
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
