from unittest.mock import MagicMock

from django.test import TestCase

from simulator.services.dto import BatterStats
from simulator.services.player_service import PlayerService


class SimulatorServicesCoverageTest(TestCase):
    """Targeted tests for simulator services coverage."""

    def test_batter_stats_invalid_probabilities(self):
        """Test that BatterStats raises ValueError when probabilities sum > 1.0."""
        # Create stats that will result in probabilities > 1.0
        # e.g. hits + strikeouts > plate_appearances
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
