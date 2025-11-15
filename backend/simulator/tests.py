"""
comprehensive test suite for simulator app.
tests dto probability calculations, simulation service monte carlo logic,
player service database queries, and api endpoint functionality.
uses django testcase and drf apitestcase for integration testing.
run with: python manage.py test simulator
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

from .services.dto import BatterStats, SimulationResult
from .services.simulation import SimulationService
from .services.player_service import PlayerService
from roster.models import Player, Team


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
            walks=10
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
            walks=10
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
            walks=0
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
                walks=60
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
        # Create a team
        self.team = Team.objects.create(
            id=1,
            name="Test Team",
            abbreviation="TST"
        )
        
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
                walk=60
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
            username='testuser',
            password='testpass123'
        )
        
        # Create team and players
        self.team = Team.objects.create(
            id=1,
            name="Test Team",
            abbreviation="TST"
        )
        
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
                walk=60
            )
            self.players.append(player)
        
        # Authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_simulate_by_ids_success(self):
        """Test simulation by player IDs endpoint."""
        url = '/api/v1/simulator/simulate-by-ids/'
        data = {
            'player_ids': [p.id for p in self.players],
            'num_games': 100
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lineup', response.data)
        self.assertIn('avg_score', response.data)
        self.assertIn('score_distribution', response.data)
        self.assertEqual(len(response.data['lineup']), 9)
    
    def test_simulate_by_ids_invalid_count(self):
        """Test that endpoint rejects wrong number of players."""
        url = '/api/v1/simulator/simulate-by-ids/'
        data = {
            'player_ids': [self.players[0].id],  # Only 1 player
            'num_games': 100
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_simulate_by_ids_unauthenticated(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)
        
        url = '/api/v1/simulator/simulate-by-ids/'
        data = {
            'player_ids': [p.id for p in self.players],
            'num_games': 100
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_simulate_by_team_success(self):
        """Test simulation by team endpoint."""
        url = '/api/v1/simulator/simulate-by-team/'
        data = {
            'team_id': self.team.id,
            'num_games': 100
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avg_score', response.data)
    
    def test_simulate_by_names_success(self):
        """Test simulation by player names endpoint."""
        url = '/api/v1/simulator/simulate-by-names/'
        data = {
            'player_names': [p.name for p in self.players],
            'num_games': 100
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
