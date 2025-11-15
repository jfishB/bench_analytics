"""
Application layer: Orchestrates simulation use cases.
Contains business logic but no infrastructure concerns.
"""

import statistics
from typing import List

from simulator.domain.entities import BatterStats, SimulationResult
from simulator.batter import Batter
from simulator.baseball import Game


class SimulationService:
    """Service for running baseball game simulations."""
    
    def simulate_lineup(
        self, 
        batter_stats: List[BatterStats], 
        num_games: int = 1000
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
    
    def compare_lineups(
        self,
        lineup_list: List[List[BatterStats]],
        num_games: int = 1000
    ) -> List[SimulationResult]:
        """
        Compare multiple lineup configurations.
        
        Args:
            lineup_list: List of lineups, each with 9 BatterStats
            num_games: Number of games to simulate per lineup
            
        Returns:
            List of SimulationResults, one per lineup
        """
        results = []
        for lineup in lineup_list:
            result = self.simulate_lineup(lineup, num_games)
            results.append(result)
        return results
