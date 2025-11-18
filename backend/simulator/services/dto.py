"""
data transfer objects for moving data between layers.
batterstats converts raw player stats into simulation probabilities.
simulationresult holds monte carlo output (avg, median, std dev, all scores).
used by player_service.py (creates batterstats from db) and 
simulation.py (creates simulationresult from games).
"""

from dataclasses import dataclass
from typing import List


@dataclass
class BatterStats:
    """Raw batting statistics for a player."""

    name: str
    plate_appearances: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    strikeouts: int
    walks: int

    @property
    def singles(self) -> int:
        """Calculate singles from total hits minus extra-base hits."""
        return self.hits - self.doubles - self.triples - self.home_runs

    def to_probabilities(self) -> List[float]:
        """
        Convert raw stats to at-bat outcome probabilities.
        Validates that probabilities don't exceed 1.0 (data quality check).

        Returns list of 7 probabilities: [K, out, walk, 1B, 2B, 3B, HR]

        Raises:
            ValueError: If outcome counts exceed plate appearances (invalid data)
        """
        if self.plate_appearances == 0:
            # Default to all outs if no data
            return [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        pa = self.plate_appearances

        prob_strikeout = self.strikeouts / pa
        prob_walk = self.walks / pa
        prob_single = self.singles / pa
        prob_double = self.doubles / pa
        prob_triple = self.triples / pa
        prob_homerun = self.home_runs / pa

        # Calculate sum to validate data quality
        prob_sum = prob_strikeout + prob_walk + prob_single + prob_double + prob_triple + prob_homerun

        # Check for data inconsistency (probabilities exceeding 1.0)
        if prob_sum > 1.0 + 1e-8:  # Allow tiny floating point error
            raise ValueError(
                f"Invalid data for player '{self.name}': outcome probabilities sum to {prob_sum:.6f} (> 1.0). "
                f"This indicates counting stats exceed plate appearances. Check data integrity."
            )

        # Remaining probability is in-play outs
        prob_out = 1.0 - prob_sum

        # Ensure non-negative (handle floating point precision)
        prob_out = max(0.0, prob_out)

        return [
            prob_strikeout,
            prob_out,
            prob_walk,
            prob_single,
            prob_double,
            prob_triple,
            prob_homerun,
        ]


@dataclass
class SimulationResult:
    """Results from a lineup simulation."""

    lineup_names: List[str]
    num_games: int
    avg_score: float
    median_score: float
    std_dev: float
    all_scores: List[int]

    def __str__(self) -> str:
        return (
            f"Simulation Results ({self.num_games} games):\n"
            f"  Average Score: {self.avg_score:.2f}\n"
            f"  Median Score: {self.median_score:.1f}\n"
            f"  Std Deviation: {self.std_dev:.2f}\n"
            f"  Lineup: {', '.join(self.lineup_names)}"
        )
