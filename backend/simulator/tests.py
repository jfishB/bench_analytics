"""
comprehensive test suite for simulator app.
tests dto probability calculations, simulation service monte carlo logic,
player service database queries, and api endpoint functionality.
uses django testcase and drf apitestcase for integration testing.
run with: python manage.py test simulator
"""

import sys
from pathlib import Path

import numpy as np
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from roster.models import Player, Team

from .services.dto import BatterStats, SimulationResult
from .services.player_service import PlayerService
from .services.simulation import SimulationService

# Add baseball-simulator library to path for game simulator tests
lib_path = Path(__file__).resolve().parent.parent / "lib" / "baseball-simulator"
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))


class BatterStatsTestCase(TestCase):
    """Test BatterStats DTO and probability calculations."""

    def test_singles_calculation(self):
        """Test that singles are calculated correctly."""
        stats = BatterStats(
            name="Test Player",
            plate_appearances=100,
            hits=30,
            doubles=5,
            triples=1,
            home_runs=4,
            strikeouts=20,
            walks=10,
        )
        # Singles = Hits - Doubles - Triples - HRs = 30 - 5 - 1 - 4 = 20
        self.assertEqual(stats.singles, 20)

    def test_to_probabilities_valid_stats(self):
        """Test probability conversion with valid stats."""
        stats = BatterStats(
            name="Test Player",
            plate_appearances=100,
            hits=30,
            doubles=5,
            triples=1,
            home_runs=4,
            strikeouts=20,
            walks=10,
        )
        probs = stats.to_probabilities()

        # Should have 7 probabilities
        self.assertEqual(len(probs), 7)

        # Probabilities should sum to ~1.0
        self.assertAlmostEqual(sum(probs), 1.0, places=5)

        # Check individual probabilities
        self.assertAlmostEqual(probs[0], 0.20, places=2)  # Strikeout
        self.assertAlmostEqual(probs[2], 0.10, places=2)  # Walk
        self.assertAlmostEqual(probs[6], 0.04, places=2)  # Home run

    def test_to_probabilities_zero_pa(self):
        """Test probability conversion with zero plate appearances."""
        stats = BatterStats(
            name="Rookie",
            plate_appearances=0,
            hits=0,
            doubles=0,
            triples=0,
            home_runs=0,
            strikeouts=0,
            walks=0,
        )
        probs = stats.to_probabilities()

        # Should default to all outs
        self.assertEqual(probs[1], 1.0)  # 100% outs
        self.assertEqual(sum(probs), 1.0)


class SimulationServiceTestCase(TestCase):
    """Test SimulationService business logic."""

    def setUp(self):
        """Create test data."""
        self.service = SimulationService()

        # Create 9 average players
        self.lineup = []
        for i in range(9):
            stats = BatterStats(
                name=f"Player {i+1}",
                plate_appearances=600,
                hits=150,
                doubles=30,
                triples=3,
                home_runs=20,
                strikeouts=120,
                walks=60,
            )
            self.lineup.append(stats)

    def test_simulate_lineup_success(self):
        """Test successful lineup simulation."""
        result = self.service.simulate_lineup(self.lineup, num_games=100)

        # Check result structure
        self.assertIsInstance(result, SimulationResult)
        self.assertEqual(len(result.lineup_names), 9)
        self.assertEqual(result.num_games, 100)
        self.assertEqual(len(result.all_scores), 100)

        # Check statistics are reasonable
        self.assertGreater(result.avg_score, 0)
        self.assertGreater(result.median_score, 0)
        self.assertGreaterEqual(result.std_dev, 0)

    def test_simulate_lineup_wrong_number_of_players(self):
        """Test that simulation fails with wrong number of players."""
        with self.assertRaises(ValueError) as context:
            self.service.simulate_lineup(self.lineup[:8], num_games=10)

        self.assertIn("exactly 9 batters", str(context.exception))

    def test_simulate_lineup_deterministic_stats(self):
        """Test that more games produces more stable statistics (lower standard error)."""
        # Run with few games
        result_small = self.service.simulate_lineup(self.lineup, num_games=10)

        # Run with many games
        result_large = self.service.simulate_lineup(self.lineup, num_games=1000)

        # Calculate Standard Error of the Mean (SEM)
        # SEM = std_dev / sqrt(n)
        # This represents the uncertainty in the average score and should decrease with N
        sem_small = result_small.std_dev / np.sqrt(result_small.num_games)
        sem_large = result_large.std_dev / np.sqrt(result_large.num_games)

        # Larger sample should have lower standard error (more precise mean)
        self.assertGreater(sem_small, sem_large)


class SimulationFlowTestCase(TestCase):
    """Test SimulationService.run_simulation_flow orchestration."""

    def setUp(self):
        self.service = SimulationService()
        self.team = Team.objects.create(id=1)
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"P{i}",
                team=self.team,
                pa=500,
                hit=100,
                double=20,
                triple=2,
                home_run=10,
                strikeout=100,
                walk=50
            )
            self.players.append(p)

    def test_flow_by_ids(self):
        """Test flow with IDs."""
        ids = [p.id for p in self.players]
        result = self.service.run_simulation_flow(ids, num_games=10, fetch_method="ids")
        self.assertIsInstance(result, SimulationResult)
        self.assertEqual(len(result.lineup_names), 9)

    def test_flow_by_names(self):
        """Test flow with names."""
        names = [p.name for p in self.players]
        result = self.service.run_simulation_flow(names, num_games=10, fetch_method="names")
        self.assertIsInstance(result, SimulationResult)

    def test_flow_by_team(self):
        """Test flow with team ID."""
        result = self.service.run_simulation_flow(self.team.id, num_games=10, fetch_method="team")
        self.assertIsInstance(result, SimulationResult)

    def test_flow_invalid_method(self):
        """Test invalid fetch method."""
        with self.assertRaises(ValueError):
            self.service.run_simulation_flow([], 10, "invalid")

    def test_flow_team_not_enough_players(self):
        """Test team with insufficient players."""
        empty_team = Team.objects.create(id=2)
        # Add one player so we don't get "No players found" error
        Player.objects.create(name="Lonely Player", team=empty_team, pa=100)
        with self.assertRaises(ValueError) as ctx:
            self.service.run_simulation_flow(empty_team.id, 10, "team")
        self.assertIn("Need exactly 9", str(ctx.exception))


class PlayerServiceTestCase(TestCase):
    """Test PlayerService data access layer."""

    def setUp(self):
        """Create test database records."""
        # Create a team (Team model no longer stores name/abbreviation)
        self.team = Team.objects.create(id=1)

        # Create test players
        self.players = []
        for i in range(10):
            player = Player.objects.create(
                name=f"Test Player {i+1}",
                team=self.team,
                pa=600 - (i * 50),  # Decreasing PAs
                hit=150,
                double=30,
                triple=3,
                home_run=20,
                strikeout=120,
                walk=60,
            )
            self.players.append(player)

        self.service = PlayerService()

    def test_get_players_by_ids_success(self):
        """Test fetching players by IDs."""
        player_ids = [p.id for p in self.players[:9]]
        batter_stats = self.service.get_players_by_ids(player_ids)

        self.assertEqual(len(batter_stats), 9)
        self.assertIsInstance(batter_stats[0], BatterStats)
        self.assertEqual(batter_stats[0].name, "Test Player 1")

    def test_get_players_by_ids_maintains_order(self):
        """Test that player order is preserved."""
        player_ids = [self.players[5].id, self.players[2].id, self.players[8].id]
        batter_stats = self.service.get_players_by_ids(player_ids)

        self.assertEqual(batter_stats[0].name, "Test Player 6")
        self.assertEqual(batter_stats[1].name, "Test Player 3")
        self.assertEqual(batter_stats[2].name, "Test Player 9")

    def test_get_players_by_ids_not_found(self):
        """Test error when player not found."""
        with self.assertRaises(ValueError) as context:
            self.service.get_players_by_ids([99999])

        self.assertIn("not found", str(context.exception))

    def test_get_players_by_names_success(self):
        """Test fetching players by names."""
        names = [p.name for p in self.players[:3]]
        batter_stats = self.service.get_players_by_names(names)

        self.assertEqual(len(batter_stats), 3)
        self.assertEqual(batter_stats[0].name, names[0])

    def test_get_team_players_success(self):
        """Test fetching team's top players."""
        batter_stats = self.service.get_team_players(self.team.id, limit=9)

        # Should get top 9 by PA
        self.assertEqual(len(batter_stats), 9)

        # Should be ordered by PA (descending)
        self.assertEqual(batter_stats[0].plate_appearances, 600)
        self.assertEqual(batter_stats[8].plate_appearances, 200)

    def test_get_team_players_not_found(self):
        """Test error when team has no players."""
        with self.assertRaises(ValueError) as context:
            self.service.get_team_players(99999)

        self.assertIn("No players found", str(context.exception))


class SimulatorAPITestCase(APITestCase):
    """Test REST API endpoints."""

    def setUp(self):
        """Set up test client and authentication."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Create team and players (Team has no name/abbreviation)
        self.team = Team.objects.create(id=1)

        self.players = []
        for i in range(9):
            player = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                pa=600,
                hit=150,
                double=30,
                triple=3,
                home_run=20,
                strikeout=120,
                walk=60,
            )
            self.players.append(player)

        # Authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_simulate_by_ids_success(self):
        """Test simulation by player IDs endpoint."""
        url = "/api/v1/simulator/simulate-by-ids/"
        data = {"player_ids": [p.id for p in self.players], "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("lineup", response.data)
        self.assertIn("avg_score", response.data)
        self.assertIn("score_distribution", response.data)
        self.assertEqual(len(response.data["lineup"]), 9)

    def test_simulate_by_ids_invalid_count(self):
        """Test that endpoint rejects wrong number of players."""
        url = "/api/v1/simulator/simulate-by-ids/"
        data = {"player_ids": [self.players[0].id], "num_games": 100}  # Only 1 player

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_simulate_by_ids_unauthenticated(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)

        url = "/api/v1/simulator/simulate-by-ids/"
        data = {"player_ids": [p.id for p in self.players], "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simulate_by_team_success(self):
        """Test simulation by team endpoint."""
        url = "/api/v1/simulator/simulate-by-team/"
        data = {"team_id": self.team.id, "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("avg_score", response.data)

    def test_simulate_by_names_success(self):
        """Test simulation by player names endpoint."""
        url = "/api/v1/simulator/simulate-by-names/"
        data = {"player_names": [p.name for p in self.players], "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simulate_by_ids_player_not_found(self):
        """Test simulation with non-existent player ID."""
        url = "/api/v1/simulator/simulate-by-ids/"
        invalid_ids = [99999] * 9  # 9 non-existent IDs
        data = {"player_ids": invalid_ids, "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_simulate_by_names_player_not_found(self):
        """Test simulation with non-existent player name."""
        url = "/api/v1/simulator/simulate-by-names/"
        invalid_names = ["NonExistent Player"] * 9
        data = {"player_names": invalid_names, "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_simulate_by_team_no_players(self):
        """Test simulation with team that has no players."""
        empty_team = Team.objects.create(id=999)
        url = "/api/v1/simulator/simulate-by-team/"
        data = {"team_id": empty_team.id, "num_games": 100}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class ParallelGameIntegrationTests(TestCase):
    """Integration tests for ParallelGame comparing statistics."""

    def setUp(self):
        """Import ParallelGame."""
        from batter import Batter  # type: ignore
        from parallel_game import ParallelGame  # type: ignore

        self.Batter = Batter
        self.ParallelGame = ParallelGame

    def test_simulation_produces_reasonable_scores(self):
        """Test that simulations produce reasonable average scores."""
        # Create a decent batting lineup (better than average)
        good_probs = [0.20, 0.30, 0.10, 0.20, 0.10, 0.05, 0.05]
        batter = self.Batter(probabilities=good_probs, name="GoodBatter")
        lineup = [batter] * 9

        game = self.ParallelGame(lineup=lineup, num_games=1000)
        game.play()
        scores = game.get_scores()

        avg_score = np.mean(scores)

        # Good lineup should score between 8-18 runs per game
        # (Note: The original Game class allows for high scoring with good lineups)
        self.assertGreater(avg_score, 8.0, "Average score too low")
        self.assertLess(avg_score, 18.0, "Average score unrealistically high")

    def test_weak_lineup_scores_less(self):
        """Test that a weak lineup scores fewer runs."""
        # Weak batting lineup (lots of strikeouts/outs)
        weak_probs = [0.30, 0.50, 0.05, 0.10, 0.03, 0.01, 0.01]
        batter = self.Batter(probabilities=weak_probs, name="WeakBatter")
        lineup = [batter] * 9

        game = self.ParallelGame(lineup=lineup, num_games=1000)
        game.play()
        scores = game.get_scores()

        avg_score = np.mean(scores)

        # Weak lineup should score 1-4 runs on average
        self.assertGreater(avg_score, 1.0)
        self.assertLess(avg_score, 4.0, "Weak lineup scoring too much")

    def test_all_games_complete(self):
        """Test that all games run to completion."""
        probs = [0.15, 0.35, 0.10, 0.20, 0.10, 0.05, 0.05]
        batter = self.Batter(probabilities=probs, name="TestBatter")
        lineup = [batter] * 9

        num_games = 100
        game = self.ParallelGame(lineup=lineup, num_games=num_games)
        game.play()
        scores = game.get_scores()

        # Should get exactly num_games scores
        self.assertEqual(len(scores), num_games)

        # All scores should be non-negative integers
        for score in scores:
            self.assertGreaterEqual(score, 0)
            self.assertIsInstance(score, (int, np.integer))

    def test_parallel_speedup(self):
        """Test that parallel execution uses multiple cores."""
        probs = [0.15, 0.35, 0.10, 0.20, 0.10, 0.05, 0.05]
        batter = self.Batter(probabilities=probs, name="TestBatter")
        lineup = [batter] * 9

        # Run with 1 process vs multiple processes
        # We can't easily time this in tests, but we can verify both work
        game_single = self.ParallelGame(lineup=lineup, num_games=100, num_processes=1)
        game_single.play()
        scores_single = game_single.get_scores()

        game_multi = self.ParallelGame(lineup=lineup, num_games=100, num_processes=4)
        game_multi.play()
        scores_multi = game_multi.get_scores()

        # Both should complete and produce 100 games
        self.assertEqual(len(scores_single), 100)
        self.assertEqual(len(scores_multi), 100)

        # Averages should be similar (within reasonable variance)
        avg_single = np.mean(scores_single)
        avg_multi = np.mean(scores_multi)

        # Both should be in a reasonable range (6-16 runs for this lineup)
        self.assertGreater(avg_single, 6.0)
        self.assertGreater(avg_multi, 6.0)
        self.assertLess(avg_single, 16.0)
        self.assertLess(avg_multi, 16.0)


from unittest.mock import MagicMock, patch
from simulator.views import _handle_simulation_request

class SimulatorViewsCoverageTest(TestCase):
    """Targeted tests for simulator/views.py coverage."""

    def setUp(self):
        self.client = APIClient()

    @patch("simulator.views.SimulationService")
    def test_handle_simulation_request_empty_results(self, mock_service_cls):
        """Test _handle_simulation_request when simulation returns no scores."""
        # Setup mock service
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        # Setup mock result with empty scores
        mock_result = MagicMock()
        mock_result.all_scores = []  # Empty list triggers the error
        mock_service.run_simulation_flow.return_value = mock_result

        # Call the helper directly
        response = _handle_simulation_request([1, 2, 3], 100, "ids")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Simulation produced no results", response.data["error"])

    @patch("simulator.views.SimulationService")
    def test_handle_simulation_request_unexpected_error(self, mock_service_cls):
        """Test _handle_simulation_request when an unexpected exception occurs."""
        # Setup mock to raise generic exception
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.run_simulation_flow.side_effect = Exception("Unexpected boom")

        # Call the helper directly
        response = _handle_simulation_request([1, 2, 3], 100, "ids")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("An unexpected error occurred", response.data["error"])
        self.assertIn("Unexpected boom", response.data["detail"])

    def test_simulate_by_player_names_invalid_serializer(self):
        """Test simulate_by_player_names with invalid data."""
        # Missing player_names
        data = {"num_games": 100}
        
        # We need a user to authenticate
        user = User.objects.create_user(username="testuser_cov", password="password")
        self.client.force_authenticate(user=user)

        url = "/api/v1/simulator/simulate-by-names/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("player_names", response.data)

    def test_simulate_by_team_invalid_serializer(self):
        """Test simulate_by_team with invalid data."""
        # Missing team_id
        data = {"num_games": 100}
        
        user = User.objects.create_user(username="testuser2_cov", password="password")
        self.client.force_authenticate(user=user)

        url = "/api/v1/simulator/simulate-by-team/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_id", response.data)


class SimulatorServicesCoverageTest(TestCase):
    """Targeted tests for simulator services coverage."""

    def test_batter_stats_invalid_probabilities(self):
        """Test that BatterStats raises ValueError when probabilities sum > 1.0."""
        # Create stats that will result in probabilities > 1.0
        stats = BatterStats(
            name="Impossible Player",
            plate_appearances=10,
            hits=5,
            doubles=0,
            triples=0,
            home_runs=0,
            strikeouts=6,  # 5 + 6 = 11 > 10
            walks=0
        )
        
        with self.assertRaises(ValueError) as cm:
            stats.to_probabilities()
        
        self.assertIn("Invalid data for player", str(cm.exception))
        self.assertIn("probabilities sum to", str(cm.exception))

    def test_convert_to_batter_stats_zero_pa(self):
        """Test _convert_to_batter_stats with 0 plate appearances."""
        service = PlayerService()
        
        # Mock a player object
        mock_player = MagicMock()
        mock_player.name = "Bench Warmer"
        mock_player.pa = 0
        
        with self.assertRaises(ValueError) as cm:
            service._convert_to_batter_stats(mock_player)
            
        self.assertIn("has no plate appearances", str(cm.exception))

    def test_batter_stats_zero_pa_default(self):
        """Test BatterStats.to_probabilities with 0 PA returns default outs."""
        stats = BatterStats(
            name="No PA Player",
            plate_appearances=0,
            hits=0,
            doubles=0,
            triples=0,
            home_runs=0,
            strikeouts=0,
            walks=0
        )
        
        probs = stats.to_probabilities()
        # Should be [K, out, walk, 1B, 2B, 3B, HR]
        # Default is [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.assertEqual(probs, [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
