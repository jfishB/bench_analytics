##########################################
"""
- This file contains the core algorithm
logic for creating batting lineups.
"""
###########################################

from typing import Dict, List

from django.contrib.auth import get_user_model
from django.db import transaction

from lineups.models import Lineup, LineupPlayer
from lineups.services.validator import validate_data
from roster.models import Player


def normalize_stat(values: List[float], invert: bool = False) -> Dict[int, float]:
    """Normalize a list of stat values to 0-1 scale.

    Args:
        values: List of stat values
        invert: If True, invert the scale (lower is better, e.g., K%)

    Returns:
        Dictionary mapping index to normalized value
    """
    # Handle cases where all values are None or empty
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return {i: 0.5 for i in range(len(values))}

    min_val = min(valid_values)
    max_val = max(valid_values)

    # Avoid division by zero
    if max_val == min_val:
        return {i: 1.0 for i in range(len(values))}

    normalized = {}
    for i, val in enumerate(values):
        if val is None:
            normalized[i] = 0.0  # Treat missing stats as worst
        else:
            norm_val = (val - min_val) / (max_val - min_val)
            normalized[i] = (1 - norm_val) if invert else norm_val

    return normalized


def calculate_spot_scores(players_list: List[Player], spot: int) -> List[float]:
    """Calculate scores for each player for a specific lineup spot.

    Args:
        players_list: List of Player objects with stats
        spot: Lineup spot number (1-9)

    Returns:
        List of scores (one per player)
    """
    n = len(players_list)

    # Extract and normalize all relevant stats
    obp = normalize_stat([p.on_base_percent for p in players_list])
    slg = normalize_stat([p.slg_percent for p in players_list])
    iso = normalize_stat([p.isolated_power for p in players_list])
    woba = normalize_stat([p.woba for p in players_list])
    bb_pct = normalize_stat([p.bb_percent for p in players_list])
    k_pct = normalize_stat(
        [p.k_percent for p in players_list], invert=True
    )  # Lower is better
    barrel_pct = normalize_stat([p.barrel_batted_rate for p in players_list])
    hard_hit_pct = normalize_stat([p.hard_hit_percent for p in players_list])
    sprint_speed = normalize_stat([p.sprint_speed for p in players_list])
    hr_rate = normalize_stat([p.home_run for p in players_list])
    sb = normalize_stat([p.r_total_stolen_base for p in players_list])

    scores = []

    for i in range(n):
        if spot == 1:
            # Leadoff: High OBP, speed, stolen bases, walks
            score = (
                0.50 * obp[i]
                + 0.20 * sprint_speed[i]
                + 0.15 * sb[i]
                + 0.10 * bb_pct[i]
                + 0.05 * k_pct[i]
            )

        elif spot == 2:
            # Elite balanced hitter: wOBA, OBP, walks, avoid strikeouts
            score = 0.4 * woba[i] + 0.3 * obp[i] + 0.2 * bb_pct[i] + 0.1 * k_pct[i]

        elif spot == 3:
            # Strong consistent hitter: wOBA, SLG, walks
            score = 0.45 * woba[i] + 0.25 * slg[i] + 0.2 * bb_pct[i] + 0.1 * k_pct[i]

        elif spot == 4:
            # Cleanup (power hitter): ISO, SLG, barrels, hard hits, HR rate
            score = (
                0.3 * iso[i]
                + 0.25 * slg[i]
                + 0.2 * barrel_pct[i]
                + 0.15 * hard_hit_pct[i]
                + 0.1 * hr_rate[i]
            )

        elif spot == 5:
            # Secondary power hitter: SLG, ISO, wOBA, barrels
            score = (
                0.35 * slg[i] + 0.25 * iso[i] + 0.25 * woba[i] + 0.15 * barrel_pct[i]
            )

        elif spot == 6:
            # Decent hitter with speed and baserunning: OBP, sprint speed, stolen bases, wOBA
            score = (
                0.35 * obp[i] + 0.25 * sprint_speed[i] + 0.20 * sb[i] + 0.20 * woba[i]
            )

        elif spot in [7, 8]:
            # Average hitters: wOBA as primary metric
            score = woba[i]

        else:  # spot == 9
            # Weakest hitter: wOBA (will select lowest)
            score = woba[i]

        scores.append(score)

    return scores


def algorithm_create_lineup(payload):
    """Create a batting lineup based on the provided payload.

    This function contains the core logic for creating a batting lineup.
    It validates the input data, applies the lineup algorithm, and returns
    the created lineup.

    Args:
        payload (CreateLineupInput): The input data for creating the lineup.

    Returns:
        Lineup: The created Lineup model instance with assigned batting orders.
    """
    # Validate and get processed data
    validated = validate_data(payload)
    team_obj = validated["team"]
    players_list = validated["players"]
    opp_pitcher = validated["opp_pitcher"]
    created_by_id = validated["created_by_id"]

    # Build position mapping from payload
    position_map = {p.player_id: p.position for p in payload.players}

    # Greedy assignment algorithm
    available_indices = set(range(len(players_list)))
    assignments = {}  # batting_order -> player_index

    for spot in range(1, 10):  # Spots 1 through 9
        # Calculate scores for all available players for this spot
        scores = calculate_spot_scores(players_list, spot)

        # Find the best available player for this spot
        best_idx = None
        best_score = -float("inf") if spot != 9 else float("inf")

        for idx in available_indices:
            if spot == 9:
                # For spot 9, we want the LOWEST score (worst hitter)
                if scores[idx] < best_score:
                    best_score = scores[idx]
                    best_idx = idx
            else:
                # For spots 1-8, we want the HIGHEST score
                if scores[idx] > best_score:
                    best_score = scores[idx]
                    best_idx = idx

        # Assign this player to this spot
        if best_idx is not None:
            assignments[spot] = best_idx
            available_indices.remove(best_idx)

    # Create the Lineup and LineupPlayer objects in a transaction
    with transaction.atomic():
        User = get_user_model()
        created_by = User.objects.get(pk=created_by_id)

        lineup = Lineup.objects.create(
            team=team_obj,
            name=payload.name,
            opponent_pitcher=opp_pitcher,
            opponent_team_id=payload.opponent_team_id,
            created_by=created_by,
        )

        # Create LineupPlayer entries
        for batting_order, player_idx in assignments.items():
            player = players_list[player_idx]
            position = position_map.get(player.id, player.position)

            LineupPlayer.objects.create(
                lineup=lineup,
                player=player,
                position=position,
                batting_order=batting_order,
            )

    return lineup
