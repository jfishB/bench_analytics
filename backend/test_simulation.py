"""
Quick test script to verify the simulator works with real data.
Tests the first 9 batters from the Blue Jays CSV file.
"""

import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from simulator.services.dto import BatterStats
from simulator.services.simulation import SimulationService


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
            walks=walks,
        )
        lineup.append(stats)

        # Show player stats
        avg = hits / pa if pa > 0 else 0
        print(
            f"{i}. {name:30s} PA:{pa:3d}  AVG:.{int(avg*1000):03d}  HR:{hrs:2d}  K:{ks:3d}  BB:{walks:2d}"
        )

    # Run simulation
    print("\n" + "=" * 70)
    print("RUNNING SIMULATION...")
    print("=" * 70)

    service = SimulationService()
    num_games = 5000

    print(f"Simulating {num_games:,} games...\n")
    result = service.simulate_lineup(lineup, num_games=num_games)

    # Display results
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Games Simulated:    {result.num_games:,}")
    print(f"Average Score:      {result.avg_score:.2f} runs/game")
    print(f"Median Score:       {result.median_score:.1f} runs/game")
    print(f"Std Deviation:      {result.std_dev:.2f}")
    print(f"Score Range:        {min(result.all_scores)} - {max(result.all_scores)} runs")

    # Show score distribution
    print("\n📈 SCORE DISTRIBUTION (Top 15):")
    print("-" * 70)

    score_counts = {}
    for score in result.all_scores:
        score_counts[score] = score_counts.get(score, 0) + 1

    for score in sorted(score_counts.keys())[:15]:
        count = score_counts[score]
        pct = (count / len(result.all_scores)) * 100
        bar_length = int(pct / 2)
        bar = "█" * bar_length
        print(f"  {score:2d} runs: {bar:25s} {pct:5.1f}% ({count:4d} games)")

    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
