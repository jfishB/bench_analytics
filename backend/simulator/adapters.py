"""
Adapters to convert bench_analytics Player model to baseball-simulator Batter objects.
"""

from batter import Batter
from baseball import Game


def player_to_batter(player) -> Batter:
    """
    Convert a roster.models.Player to a baseball.Batter.

    Maps stats like woba, k_percent, bb_percent to at-bat probabilities.
    Uses woba as the primary indicator of hitting skill.
    """
    name = player.name

    # Extract stats (with fallbacks to 0)
    k_percent = (player.k_percent or 0) / 100.0  # Convert % to decimal
    bb_percent = (player.bb_percent or 0) / 100.0

    # Estimate probabilities for: K, out, walk, 1B, 2B, 3B, HR
    # Based on available stats
    prob_k = min(k_percent, 0.4)  # Cap at 0.4 (40%)
    prob_walk = min(bb_percent, 0.2)  # Cap at 0.2 (20%)

    # Remaining probability to distribute among hits
    prob_hit = 1.0 - prob_k - prob_walk - 0.35  # Reserve ~35% for outs
    prob_out = max(0.1, 0.35)  # At least 10% outs

    # Normalize hits
    if prob_hit > 0:
        # Use isolated_power and other stats to estimate hit distribution
        prob_hr = min((player.isolated_power or 0) / 0.3, prob_hit * 0.15)  # HR as % of hit rate
        prob_3b = max(0.005, prob_hit * 0.02)
        prob_2b = max(0.04, prob_hit * 0.15)
        prob_1b = prob_hit - prob_hr - prob_3b - prob_2b
    else:
        prob_hr = prob_3b = prob_2b = prob_1b = 0.0

    # Create Batter with calculated probabilities
    probabilities = [prob_k, prob_out, prob_walk, prob_1b, prob_2b, prob_3b, prob_hr]

    # Ensure probabilities sum to ~1.0
    total = sum(probabilities)
    if total > 0:
        probabilities = [p / total for p in probabilities]

    return Batter(probabilities=probabilities, name=name)


def simulate_lineup(players, num_games=1000):
    """
    Simulate a lineup of Player objects across multiple games.

    Returns: (avg_score, median_score, std_dev, all_scores)
    """
    from baseball import Game

    # Convert players to batters
    lineup = [player_to_batter(p) for p in players]

    if len(lineup) != 9:
        raise ValueError(f"Lineup must have exactly 9 players, got {len(lineup)}")

    scores = []
    for _ in range(num_games):
        game = Game(lineup=lineup)
        game.play()
        scores.append(game.score)

    import statistics

    avg_score = statistics.mean(scores)
    median_score = statistics.median(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0

    return avg_score, median_score, std_dev, scores


def compare_lineups(lineup_list, num_games=1000):
    """
    Compare multiple lineups and return stats for each.

    lineup_list: List of lists, each containing 9 Player objects

    Returns: List of (lineup_idx, avg_score, median_score, std_dev)
    """
    results = []
    for idx, lineup in enumerate(lineup_list):
        avg, med, std, _ = simulate_lineup(lineup, num_games=num_games)
        results.append(
            {
                "lineup_index": idx,
                "avg_score": avg,
                "median_score": med,
                "std_dev": std,
            }
        )
    return results
