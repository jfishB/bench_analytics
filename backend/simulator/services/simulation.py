"""
runs monte carlo baseball simulations using bram stoker's baseball-simulator library.
source: https://github.com/BramStoker/baseball-simulator

converts batterstats dtos to batter probability objects,
runs thousands of game simulations in parallel using multiprocessing (default 10k),
calculates aggregate statistics (mean, median, std dev),
and returns simulationresult dto.
called by views.py after player_service.py fetches data.
"""

# Import Bram's baseball simulator from lib directory
# Add lib path dynamically since it's not a proper Python package
import os
import statistics
import sys
from typing import List

from .dto import BatterStats, SimulationResult
from .player_service import PlayerService

lib_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "lib", "baseball-simulator"
)
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from batter import Batter  # type: ignore
from parallel_game import ParallelGame  # type: ignore


class SimulationService:
    """Service for running baseball game simulations."""

    def simulate_lineup(
        self, batter_stats: List[BatterStats], num_games: int = 10000
    ) -> SimulationResult:
        """
        Simulate multiple games with the given lineup using parallel processing.

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

        # Run simulations in parallel across multiple CPU cores
        # This provides ~4x speedup on 4-core machines (or more on higher core counts)
        parallel_game = ParallelGame(lineup=lineup, num_games=num_games)
        parallel_game.play()
        scores = parallel_game.get_scores()

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
            all_scores=scores,
        )

    def run_simulation_flow(
        self, player_input: list | int, num_games: int, fetch_method: str
    ) -> SimulationResult:
        """
        Orchestrate the simulation flow: fetch players -> validate -> simulate.

        Args:
            player_input: List of IDs, names, or a team ID
            num_games: Number of games to simulate
            fetch_method: 'ids', 'names', or 'team'

        Returns:
            SimulationResult object

        Raises:
            ValueError: If validation fails (wrong number of players, not found, etc.)
        """
        player_service = PlayerService()

        # 1. Fetch players based on method
        if fetch_method == "ids":
            batter_stats = player_service.get_players_by_ids(player_input)
        elif fetch_method == "names":
            batter_stats = player_service.get_players_by_names(player_input)
        elif fetch_method == "team":
            batter_stats = player_service.get_team_players(player_input, limit=9)
            if len(batter_stats) < 9:
                raise ValueError(
                    f"Team {player_input} only has {len(batter_stats)} players with valid stats. Need exactly 9."
                )
        else:
            raise ValueError(f"Invalid fetch method: {fetch_method}")

        # 2. Run simulation (validation happens inside simulate_lineup)
        return self.simulate_lineup(batter_stats, num_games=num_games)

