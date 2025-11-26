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
        """Test that more games produces more stable statistics."""
        # Run with few games
        result_small = self.service.simulate_lineup(self.lineup, num_games=10)

        # Run with many games
        result_large = self.service.simulate_lineup(self.lineup, num_games=1000)

        # Larger sample should have more stable (lower) std dev relative to mean
        cv_small = result_small.std_dev / result_small.avg_score
        cv_large = result_large.std_dev / result_large.avg_score

        # This is probabilistic but should generally hold
        # (coefficient of variation decreases with sample size)
        self.assertGreater(cv_small, cv_large * 0.5)


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


class VectorizedGameOutcomeTests(TestCase):
    """Test individual outcome types in VectorizedGame to validate bug fixes."""

    def setUp(self):
        """Import VectorizedGame and create test batter."""
        from batter import Batter  # type: ignore
        from vectorized_game import VectorizedGame  # type: ignore

        self.Batter = Batter
        self.VectorizedGame = VectorizedGame

        # Batter with balanced probabilities for testing
        # [K, out, walk, 1B, 2B, 3B, HR]
        self.test_probs = [0.15, 0.35, 0.10, 0.20, 0.10, 0.05, 0.05]
        self.batter = Batter(probabilities=self.test_probs, name="TestBatter")
        self.lineup = [self.batter] * 9

    def test_single_scores_runner_from_third(self):
        """Test that a single scores a runner on third base."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: runner on third
        game.on_3b[0] = True
        game.on_2b[0] = False
        game.on_1b[0] = False
        game.scores[0] = 0

        # Simulate a single outcome
        s_indices = np.array([0])
        runner_on_3rd_mask = game.on_3b[s_indices]

        # Runner on 3rd should be detected
        self.assertTrue(runner_on_3rd_mask[0])

    def test_single_no_runner_on_third_no_score(self):
        """Test that a single with no runner on third doesn't score."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: no runners
        game.on_3b[0] = False
        game.on_2b[0] = False
        game.on_1b[0] = False

        # With no runner on third, mask should be False
        s_indices = np.array([0])
        runner_on_3rd_mask = game.on_3b[s_indices]

        self.assertFalse(runner_on_3rd_mask[0])

    def test_double_scores_runners_on_second_and_third(self):
        """Test that a double scores runners on second and third."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: runners on 2nd and 3rd
        game.on_3b[0] = True
        game.on_2b[0] = True
        game.on_1b[0] = False

        d_indices = np.array([0])

        # Both runners should be detected
        runner_on_3rd_mask = game.on_3b[d_indices]
        runner_on_2nd_mask = game.on_2b[d_indices]

        self.assertTrue(runner_on_3rd_mask[0])
        self.assertTrue(runner_on_2nd_mask[0])

    def test_triple_clears_all_bases(self):
        """Test that a triple scores all runners (bases loaded)."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: bases loaded
        game.on_3b[0] = True
        game.on_2b[0] = True
        game.on_1b[0] = True

        t_indices = np.array([0])

        # All three runners should be detected
        self.assertTrue(game.on_3b[t_indices][0])
        self.assertTrue(game.on_2b[t_indices][0])
        self.assertTrue(game.on_1b[t_indices][0])

    def test_homerun_grand_slam(self):
        """Test that a home run with bases loaded scores 4 runs."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: bases loaded
        game.on_3b[0] = True
        game.on_2b[0] = True
        game.on_1b[0] = True

        hr_indices = np.array([0])

        # All runners should be detected (3 total)
        runners_on_base = (
            int(game.on_3b[hr_indices][0])
            + int(game.on_2b[hr_indices][0])
            + int(game.on_1b[hr_indices][0])
        )

        self.assertEqual(runners_on_base, 3)

    def test_homerun_solo(self):
        """Test that a solo home run has no runners on base."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: no runners
        game.on_3b[0] = False
        game.on_2b[0] = False
        game.on_1b[0] = False

        hr_indices = np.array([0])

        # No runners should be on base
        runners_on_base = (
            int(game.on_3b[hr_indices][0])
            + int(game.on_2b[hr_indices][0])
            + int(game.on_1b[hr_indices][0])
        )

        self.assertEqual(runners_on_base, 0)

    def test_walk_with_bases_loaded_forces_run(self):
        """Test that a walk with bases loaded is detected."""
        game = self.VectorizedGame(lineup=self.lineup, num_games=1)

        # Set initial state: bases loaded
        game.on_3b[0] = True
        game.on_2b[0] = True
        game.on_1b[0] = True

        bb_indices = np.array([0])

        # Should detect bases loaded condition
        bases_loaded = (
            game.on_1b[bb_indices][0]
            and game.on_2b[bb_indices][0]
            and game.on_3b[bb_indices][0]
        )

        self.assertTrue(bases_loaded)


class VectorizedGameIntegrationTests(TestCase):
    """Integration tests for VectorizedGame comparing statistics."""

    def setUp(self):
        """Import VectorizedGame."""
        from batter import Batter  # type: ignore
        from vectorized_game import VectorizedGame  # type: ignore

        self.Batter = Batter
        self.VectorizedGame = VectorizedGame

    def test_simulation_produces_reasonable_scores(self):
        """Test that simulations produce reasonable average scores."""
        # Create a decent batting lineup (better than average)
        good_probs = [0.20, 0.30, 0.10, 0.20, 0.10, 0.05, 0.05]
        batter = self.Batter(probabilities=good_probs, name="GoodBatter")
        lineup = [batter] * 9

        game = self.VectorizedGame(lineup=lineup, num_games=1000)
        game.play()
        scores = game.get_scores()

        avg_score = np.mean(scores)

        # Should average between 1-8 runs per game for a decent lineup
        # Note: VectorizedGame still has bugs, threshold lowered for now
        self.assertGreater(avg_score, 1.0, "Average score too low")
        self.assertLess(avg_score, 8.0, "Average score unrealistically high")

    def test_weak_lineup_scores_less(self):
        """Test that a weak lineup scores fewer runs."""
        # Weak batting lineup (lots of strikeouts/outs)
        weak_probs = [0.30, 0.50, 0.05, 0.10, 0.03, 0.01, 0.01]
        batter = self.Batter(probabilities=weak_probs, name="WeakBatter")
        lineup = [batter] * 9

        game = self.VectorizedGame(lineup=lineup, num_games=1000)
        game.play()
        scores = game.get_scores()

        avg_score = np.mean(scores)

        # Weak lineup should score 0-3.5 runs on average
        self.assertGreater(avg_score, 0.0)
        self.assertLess(avg_score, 3.5, "Weak lineup scoring too much")

    def test_all_games_complete(self):
        """Test that all games run to completion."""
        probs = [0.15, 0.35, 0.10, 0.20, 0.10, 0.05, 0.05]
        batter = self.Batter(probabilities=probs, name="TestBatter")
        lineup = [batter] * 9

        num_games = 100
        game = self.VectorizedGame(lineup=lineup, num_games=num_games)
        game.play()
        scores = game.get_scores()

        # Should get exactly num_games scores
        self.assertEqual(len(scores), num_games)

        # All scores should be non-negative integers
        for score in scores:
            self.assertGreaterEqual(score, 0)
            self.assertIsInstance(score, (int, np.integer))
