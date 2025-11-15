"""
runs monte carlo baseball simulations using bram's simulator library.
converts batterstats dtos to batter probability objects,
runs thousands of game simulations (default 10k),
calculates aggregate statistics (mean, median, std dev),
and returns simulationresult dto.
called by views.py after player_service.py fetches data.
uses lib/baseball-simulator for game mechanics.
"""

import statistics
import sys
from pathlib import Path
from typing import List

from .dto import BatterStats, SimulationResult

# Import Bram's baseball simulator from lib directory
# Add lib path dynamically since it's not a proper Python package
import os
lib_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'baseball-simulator')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from batter import Batter  # type: ignore
from baseball import Game  # type: ignore


class SimulationService:
    """Service for running baseball game simulations."""
    
    def simulate_lineup(
        self, 
        batter_stats: List[BatterStats], 
        num_games: int = 10000
    ) -> SimulationResult:
        """
        Simulate multiple games with the given lineup.
        
        Args:
            batter_stats: List of exactly 9 BatterStats objects
            num_games: Number of games to simulate
            
        Returns:
            SimulationResult with aggregate statistics
            
        Raises:
            ValueError: If lineup doesn't have exactly 9 batters
        """
        if len(batter_stats) != 9:
            raise ValueError(
                f"Lineup must have exactly 9 batters, got {len(batter_stats)}"
            )
        
        # Convert domain entities to simulator Batter objects
        lineup = []
        for stats in batter_stats:
            probabilities = stats.to_probabilities()
            batter = Batter(probabilities=probabilities, name=stats.name)
            lineup.append(batter)
        
        # Run simulations
        scores = []
        for _ in range(num_games):
            game = Game(lineup=lineup, printing=False)
            game.reset_game_state()
            game.play()
            scores.append(game.get_score())
        
        # Calculate statistics
        avg_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        return SimulationResult(
            lineup_names=[stats.name for stats in batter_stats],
            num_games=num_games,
            avg_score=avg_score,
            median_score=median_score,
            std_dev=std_dev,
            all_scores=scores
        )
