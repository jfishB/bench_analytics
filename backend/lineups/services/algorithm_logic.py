##########################################
"""
- This file contains the core algorithm
logic for creating batting lineups.

BATTING ORDER PHILOSOPHY:
- Spot 1 (Leadoff): Get on base, steal bases, score runs
- Spot 2 (Contact): Table-setter, avoid strikeouts, advance runners
- Spot 3 (Best Hitter): Most consistent, high average, gets on base
- Spot 4 (Cleanup): Power hitter, drive in runs, hit home runs
- Spot 5 (Secondary Power): Second-best power hitter
- Spot 6 (Speed/OBP): Secondary table-setter with speed
- Spot 7-8 (Average): Competent hitters
- Spot 9 (Weakest): Lowest offensive production
"""
###########################################

from typing import Dict, List

from django.contrib.auth import get_user_model
from django.db import transaction

from lineups.models import Lineup, LineupPlayer
from lineups.services.validator import validate_data
from roster.models import Player

# ============================================================================
# SPOT-SPECIFIC SCORING WEIGHTS
# These weights reflect traditional baseball lineup construction strategy
# ============================================================================

# Spot 1: Leadoff - Primary goal is to get on base and create scoring opportunities
LEADOFF_WEIGHTS = {
    "obp": 0.50,  # On-base % is critical - must get on base
    "sprint_speed": 0.20,  # Speed to steal bases and take extra bases
    "stolen_bases": 0.15,  # Proven base-stealing ability
    "walk_rate": 0.10,  # Patience to draw walks
    "k_avoid": 0.05,  # Avoiding strikeouts (less critical than OBP)
}

# Spot 2: Table-Setter - Elite balanced hitter who can hit for average and avoid outs
TABLE_SETTER_WEIGHTS = {
    "woba": 0.40,  # Overall offensive value
    "obp": 0.30,  # Must get on base consistently
    "walk_rate": 0.20,  # Patience and plate discipline
    "k_avoid": 0.10,  # Contact skills - avoiding strikeouts is key
}

# Spot 3: Best Hitter - Most consistent and productive overall hitter
BEST_HITTER_WEIGHTS = {
    "woba": 0.45,  # Highest weight on overall offensive production
    "slg": 0.25,  # Some power is valuable
    "walk_rate": 0.20,  # Plate discipline remains important
    "k_avoid": 0.10,  # Contact ability
}

# Spot 4: Cleanup (Power) - Drive in runs with extra-base hits and home runs
CLEANUP_WEIGHTS = {
    "iso": 0.30,  # Isolated power (extra-base hit ability)
    "slg": 0.25,  # Raw slugging power
    "barrel_rate": 0.20,  # Quality of contact (barrels = optimal hits)
    "hard_hit": 0.15,  # Hard contact leads to hits
    "hr_rate": 0.10,  # Home run power
}

# Spot 5: Secondary Power - Second-best power hitter, similar to cleanup but slightly less power-focused
SECONDARY_POWER_WEIGHTS = {
    "slg": 0.35,  # Slugging is primary focus
    "iso": 0.25,  # Isolated power
    "woba": 0.25,  # Overall offensive value matters
    "barrel_rate": 0.15,  # Quality contact
}

# Spot 6: Speed/OBP Hybrid - Secondary table-setter with baserunning ability
SIXTH_SPOT_WEIGHTS = {
    "obp": 0.35,  # Getting on base
    "sprint_speed": 0.25,  # Speed for baserunning
    "stolen_bases": 0.20,  # Proven speed/stealing
    "woba": 0.20,  # Overall offensive contribution
}

# Spots 7-8: Average Hitters - Use overall offensive value (wOBA) as sole metric
# These spots get the remaining competent hitters after top 6 are assigned

# Spot 9: Weakest Hitter - Pitcher spot in NL or weakest hitter in AL
# Intentionally select the LOWEST wOBA (inverse of spots 7-8)

# Sample size confidence threshold
MIN_CONFIDENT_PA = 100  # Players with < 100 PA get confidence penalty
CONFIDENCE_SCALE = 100.0  # Scale factor for PA confidence weighting

# wOBA blending ratio for predictive accuracy
WOBA_ACTUAL_WEIGHT = 0.6  # Weight for actual wOBA (what happened)
XWOBA_EXPECTED_WEIGHT = 0.4  # Weight for xwOBA (expected based on quality of contact)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def normalize_stat(values: List[float], invert: bool = False) -> Dict[int, float]:
    """Normalize a list of stat values to 0-1 scale using min-max normalization.

    Args:
        values: List of stat values
        invert: If True, invert the scale (lower is better, e.g., K%)

    Returns:
        Dictionary mapping index to normalized value (0.0 = worst, 1.0 = best)
    """
    # Handle cases where all values are None or empty
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return {i: 0.5 for i in range(len(values))}

    min_val = min(valid_values)
    max_val = max(valid_values)

    # Avoid division by zero when all values are identical
    if max_val == min_val:
        return {i: 1.0 for i in range(len(values))}

    normalized = {}
    for i, val in enumerate(values):
        if val is None:
            normalized[i] = 0.0  # Treat missing stats as worst performance
        else:
            norm_val = (val - min_val) / (max_val - min_val)
            normalized[i] = (1 - norm_val) if invert else norm_val

    return normalized


def blend_woba_xwoba(woba_norm: Dict[int, float], xwoba_norm: Dict[int, float]) -> Dict[int, float]:
    """Blend actual wOBA (60%) with expected xwOBA (40%) for predictive accuracy.

    wOBA measures actual offensive production, while xwOBA measures expected
    production based on quality of contact. Blending both provides a more
    stable and predictive measure of true offensive ability.

    Args:
        woba_norm: Normalized wOBA values (actual results)
        xwoba_norm: Normalized xwOBA values (expected based on contact quality)

    Returns:
        Dictionary mapping index to blended wOBA value
    """
    return {i: WOBA_ACTUAL_WEIGHT * woba_norm[i] + XWOBA_EXPECTED_WEIGHT * xwoba_norm[i] for i in woba_norm}


def calculate_spot_scores(players_list: List[Player], spot: int) -> List[float]:
    """Calculate optimized scores for each player for a specific lineup spot.

    Each batting order spot has a different strategic purpose in baseball,
    requiring different combinations of skills. This function calculates
    a weighted score for each player based on spot-specific requirements.

    Args:
        players_list: List of Player objects with Baseball Savant stats
        spot: Lineup spot number (1-9)

    Returns:
        List of scores (one per player), where higher = better fit for the spot
        Exception: Spot 9 uses lower = better (to select weakest hitter)
    """
    n = len(players_list)

    # ========================================================================
    # STEP 1: Extract and normalize all relevant stats to 0-1 scale
    # ========================================================================
    obp = normalize_stat([p.on_base_percent for p in players_list])
    slg = normalize_stat([p.slg_percent for p in players_list])
    iso = normalize_stat([p.isolated_power for p in players_list])

    # Blend actual and expected wOBA for stability
    woba = normalize_stat([p.woba for p in players_list])
    xwoba = normalize_stat([p.xwoba for p in players_list])
    combined_woba = blend_woba_xwoba(woba, xwoba)

    # Plate discipline metrics
    bb_pct = normalize_stat([p.bb_percent for p in players_list])
    k_pct = normalize_stat([p.k_percent for p in players_list], invert=True)  # Lower K% is better

    # Contact quality metrics
    barrel_pct = normalize_stat([p.barrel_batted_rate for p in players_list])
    hard_hit_pct = normalize_stat([p.hard_hit_percent for p in players_list])

    # Speed and baserunning metrics
    sprint_speed = normalize_stat([p.sprint_speed for p in players_list])
    sb = normalize_stat([p.r_total_stolen_base for p in players_list])

    # Power metric
    hr_rate = normalize_stat([p.home_run for p in players_list])

    # Extract PA values for sample size confidence weighting
    pa_values = [p.pa for p in players_list]

    # ========================================================================
    # STEP 2: Calculate spot-specific weighted scores
    # ========================================================================
    scores = []

    for i in range(n):
        # Apply spot-specific scoring formula based on lineup position
        if spot == 1:
            # LEADOFF: Get on base, use speed, create scoring opportunities
            score = (
                LEADOFF_WEIGHTS["obp"] * obp[i]
                + LEADOFF_WEIGHTS["sprint_speed"] * sprint_speed[i]
                + LEADOFF_WEIGHTS["stolen_bases"] * sb[i]
                + LEADOFF_WEIGHTS["walk_rate"] * bb_pct[i]
                + LEADOFF_WEIGHTS["k_avoid"] * k_pct[i]
            )

        elif spot == 2:
            # TABLE-SETTER: Elite balanced hitter, high contact, avoid Ks
            score = (
                TABLE_SETTER_WEIGHTS["woba"] * combined_woba[i]
                + TABLE_SETTER_WEIGHTS["obp"] * obp[i]
                + TABLE_SETTER_WEIGHTS["walk_rate"] * bb_pct[i]
                + TABLE_SETTER_WEIGHTS["k_avoid"] * k_pct[i]
            )

        elif spot == 3:
            # BEST HITTER: Most consistent and productive overall
            score = (
                BEST_HITTER_WEIGHTS["woba"] * combined_woba[i]
                + BEST_HITTER_WEIGHTS["slg"] * slg[i]
                + BEST_HITTER_WEIGHTS["walk_rate"] * bb_pct[i]
                + BEST_HITTER_WEIGHTS["k_avoid"] * k_pct[i]
            )

        elif spot == 4:
            # CLEANUP: Power hitter who drives in runs with XBH and HR
            score = (
                CLEANUP_WEIGHTS["iso"] * iso[i]
                + CLEANUP_WEIGHTS["slg"] * slg[i]
                + CLEANUP_WEIGHTS["barrel_rate"] * barrel_pct[i]
                + CLEANUP_WEIGHTS["hard_hit"] * hard_hit_pct[i]
                + CLEANUP_WEIGHTS["hr_rate"] * hr_rate[i]
            )

        elif spot == 5:
            # SECONDARY POWER: Second-best power hitter
            score = (
                SECONDARY_POWER_WEIGHTS["slg"] * slg[i]
                + SECONDARY_POWER_WEIGHTS["iso"] * iso[i]
                + SECONDARY_POWER_WEIGHTS["woba"] * combined_woba[i]
                + SECONDARY_POWER_WEIGHTS["barrel_rate"] * barrel_pct[i]
            )

        elif spot == 6:
            # SPEED/OBP HYBRID: Secondary table-setter with baserunning
            score = (
                SIXTH_SPOT_WEIGHTS["obp"] * obp[i]
                + SIXTH_SPOT_WEIGHTS["sprint_speed"] * sprint_speed[i]
                + SIXTH_SPOT_WEIGHTS["stolen_bases"] * sb[i]
                + SIXTH_SPOT_WEIGHTS["woba"] * combined_woba[i]
            )

        elif spot in [7, 8]:
            # AVERAGE HITTERS: Use overall offensive value (wOBA)
            # After assigning top 6 spots, these get the remaining better hitters
            score = combined_woba[i]

        else:  # spot == 9
            # WEAKEST HITTER: Select player with lowest wOBA
            # Note: We'll invert this during assignment (select min instead of max)
            score = combined_woba[i]

        # ====================================================================
        # STEP 3: Apply sample size confidence penalty
        # Players with fewer than 100 PA get their score reduced proportionally
        # Example: 50 PA -> score multiplied by 0.5, 100 PA -> score multiplied by 1.0
        # ====================================================================
        if pa_values[i] is not None and pa_values[i] < MIN_CONFIDENT_PA:
            confidence_factor = min(1.0, pa_values[i] / CONFIDENCE_SCALE)
            score *= confidence_factor

        scores.append(score)

    return scores


# ============================================================================
# MAIN ALGORITHM FUNCTION
# ============================================================================


def algorithm_create_lineup(payload):
    """Create an optimized batting lineup based on player statistics.

    This implements a greedy assignment algorithm:
    1. Validate input data (team, players, user)
    2. For each lineup spot (1-9 in order):
       - Calculate scores for all remaining unassigned players
       - Assign the best-scoring player to that spot
       - Remove player from available pool
    3. Save lineup to database

    Args:
        payload (CreateLineupInput): The input data for creating the lineup

    Returns:
        Lineup: The created Lineup model instance with assigned batting orders
    """
    # ========================================================================
    # STEP 1: Validate input and extract data
    # ========================================================================
    validated = validate_data(payload)
    team_obj = validated["team"]
    players_list = validated["players"]
    created_by_id = validated["created_by_id"]

    # Build position mapping from payload (maintains user's position assignments)
    position_map = {p.player_id: p.position for p in payload.players}

    # ========================================================================
    # STEP 2: Greedy assignment algorithm
    # ========================================================================
    available_indices = set(range(len(players_list)))
    assignments = {}  # batting_order -> player_index

    for spot in range(1, 10):  # Assign batting spots 1 through 9
        # Calculate spot-specific scores for all available players
        scores = calculate_spot_scores(players_list, spot)

        # Find the best available player for this spot
        best_idx = None
        best_score = -float("inf") if spot != 9 else float("inf")

        for idx in available_indices:
            if spot == 9:
                # For spot 9, we want the LOWEST score (weakest hitter)
                if scores[idx] < best_score:
                    best_score = scores[idx]
                    best_idx = idx
            else:
                # For spots 1-8, we want the HIGHEST score (best fit)
                if scores[idx] > best_score:
                    best_score = scores[idx]
                    best_idx = idx

        # Assign this player to this spot and mark as unavailable
        if best_idx is not None:
            assignments[spot] = best_idx
            available_indices.remove(best_idx)

    # ========================================================================
    # STEP 3: Create Lineup and LineupPlayer objects in database
    # ========================================================================
    with transaction.atomic():
        User = get_user_model()
        created_by = User.objects.get(pk=created_by_id)

        lineup = Lineup.objects.create(
            team=team_obj,
            name=payload.name,
            created_by=created_by,
        )

        # Create LineupPlayer entries for each assigned batting spot
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
