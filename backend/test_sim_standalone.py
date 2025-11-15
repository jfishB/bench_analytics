"""
Standalone test of the simulator without Django.
Tests the first 9 batters from the Blue Jays CSV file.
"""

import sys
import os
from dataclasses import dataclass
from typing import List
import statistics

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import Bram's simulator from lib
lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'baseball-simulator')
sys.path.insert(0, lib_path)

from batter import Batter
from baseball import Game


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
        
        Returns list of 7 probabilities: [K, out, walk, 1B, 2B, 3B, HR]
        """
        if self.plate_appearances == 0:
            return [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        pa = self.plate_appearances
        
        prob_strikeout = self.strikeouts / pa
        prob_walk = self.walks / pa
        prob_single = self.singles / pa
        prob_double = self.doubles / pa
        prob_triple = self.triples / pa
        prob_homerun = self.home_runs / pa
        
        # Remaining probability is in-play outs
        prob_out = 1.0 - (prob_strikeout + prob_walk + prob_single + 
                          prob_double + prob_triple + prob_homerun)
        
        # Ensure non-negative
        prob_out = max(0.0, prob_out)
        
        return [
            prob_strikeout,
            prob_out,
            prob_walk,
            prob_single,
            prob_double,
            prob_triple,
            prob_homerun
        ]


def simulate_lineup(batter_stats_list, num_games=1000):
    """Run Monte Carlo simulation."""
    # Convert to Batter objects
    lineup = []
    for stats in batter_stats_list:
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
    
    return avg_score, median_score, std_dev, scores


def main():
    print("=" * 70)
    print("TESTING SIMULATOR WITH BLUE JAYS DATA")
    print("=" * 70)
    
    # First 9 batters from test_dataset_monte_carlo_bluejays.csv
    players_data = [
        # name, PA, H, 2B, 3B, HR, SO, BB
        ("Guerrero Jr., Vladimir", 680, 172, 34, 0, 23, 94, 81),
        ("Bichette, Bo", 628, 181, 44, 1, 18, 91, 40),
        ("Clement, Ernie", 588, 151, 35, 2, 9, 61, 27),
        ("Springer, George", 586, 154, 27, 1, 32, 111, 69),
        ("Kirk, Alejandro", 506, 127, 18, 0, 15, 59, 48),
        ("Barger, Addison", 502, 112, 32, 1, 21, 121, 36),
        ("France, Ty", 490, 114, 25, 0, 7, 83, 22),
        ("Kiner-Falefa, Isiah", 459, 113, 21, 2, 2, 77, 17),
        ("Lukes, Nathan", 438, 99, 19, 2, 12, 60, 38),
    ]
    
    # Create BatterStats DTOs
    lineup = []
    print("\n📋 LINEUP:")
    for i, (name, pa, hits, doubles, triples, hrs, ks, walks) in enumerate(players_data, 1):
        stats = BatterStats(
            name=name,
            plate_appearances=pa,
            hits=hits,
            doubles=doubles,
            triples=triples,
            home_runs=hrs,
            strikeouts=ks,
            walks=walks
        )
        lineup.append(stats)
        
        # Show player stats
        avg = hits / pa if pa > 0 else 0
        obp = (hits + walks) / pa if pa > 0 else 0
        singles = stats.singles
        print(f"{i}. {name:30s} PA:{pa:3d}  AVG:.{int(avg*1000):03d}  OBP:.{int(obp*1000):03d}  1B:{singles:2d}  2B:{doubles:2d}  3B:{triples}  HR:{hrs:2d}  SO:{ks:3d}  BB:{walks:2d}")
    
    # Run simulation
    print("\n" + "=" * 70)
    print("RUNNING SIMULATION...")
    print("=" * 70)
    
    num_games = 10000
    print(f"Simulating {num_games:,} games...\n")
    
    avg_score, median_score, std_dev, all_scores = simulate_lineup(lineup, num_games=num_games)
    
    # Display results
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Games Simulated:    {num_games:,}")
    print(f"Average Score:      {avg_score:.2f} runs/game")
    print(f"Median Score:       {median_score:.1f} runs/game")
    print(f"Std Deviation:      {std_dev:.2f}")
    print(f"Score Range:        {min(all_scores)} - {max(all_scores)} runs")
    
    # Show score distribution
    print("\n📈 SCORE DISTRIBUTION (Top 15 most common):")
    print("-" * 70)
    
    score_counts = {}
    for score in all_scores:
        score_counts[score] = score_counts.get(score, 0) + 1
    
    for score in sorted(score_counts.keys())[:15]:
        count = score_counts[score]
        pct = (count / len(all_scores)) * 100
        bar_length = int(pct / 2)
        bar = "█" * bar_length
        print(f"  {score:2d} runs: {bar:25s} {pct:5.1f}% ({count:4d} games)")
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE!")
    print("=" * 70)
    
    # Show interpretation
    print("\n💡 INTERPRETATION:")
    print(f"   This lineup is expected to score ~{avg_score:.1f} runs per game")
    print(f"   Most games ({median_score:.0f} runs) fall near the median")
    print(f"   Variation is ±{std_dev:.1f} runs (1 standard deviation)")


if __name__ == "__main__":
    main()
