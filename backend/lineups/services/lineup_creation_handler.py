##########################################
"""
- This file contains service functions for handling
lineup creation requests from the view layer.
- Separates business logic from HTTP handling.
"""
###########################################

from typing import Dict, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from lineups.models import Lineup, LineupPlayer
from roster.models import Player as RosterPlayer

from .input_data import CreateLineupInput, LineupPlayerInput
from .validator import validate_batting_orders, validate_data, validate_lineup_model


def determine_request_mode(request_data: dict) -> Tuple[str, Optional[dict]]:
    """Determine if request is for manual save or algorithm generation.
    
    Args:
        request_data: The raw request data from the view
        
    Returns:
        Tuple of (mode, validated_data) where mode is either 'manual_save' or 'algorithm_generate'
    """
    from lineups.serializers import LineupCreate
    
    req_full = LineupCreate(data=request_data)
    
    if req_full.is_valid():
        data = req_full.validated_data
        players_data = data["players"]
        all_have_batting_order = all(p.get("batting_order") is not None for p in players_data)
        
        if all_have_batting_order:
            return 'manual_save', data
    
    return 'algorithm_generate', None


def handle_manual_lineup_save(data: dict, user) -> Tuple[Lineup, list]:
    """Handle manual or sabermetrics lineup save with provided batting orders.
    
    Args:
        data: Validated lineup data with players and batting orders
        user: The authenticated user making the request
        
    Returns:
        Tuple of (lineup, lineup_players)
    """
    team_id = data["team_id"]
    lineup_name = data.get("name") or f"Lineup - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    players_data = data["players"]
    
    # Build CreateLineupInput with provided batting orders
    players_input = [
        LineupPlayerInput(
            player_id=p["player_id"],
            position=p["position"],
            batting_order=p.get("batting_order"),
        )
        for p in players_data
    ]
    
    payload = CreateLineupInput(
        team_id=team_id,
        players=players_input,
        requested_user_id=(user.id if user.is_authenticated else None),
    )
    
    # Validate batting orders are unique and cover 1-9
    validate_batting_orders(payload.players)
    
    # Validate data
    validated = validate_data(payload)
    team_obj = validated["team"]
    players_list = validated["players"]
    created_by_id = validated["created_by_id"]
    
    # Build batting order and position mappings from payload
    batting_orders = {}
    position_map = {}
    for p in payload.players:
        batting_orders[p.player_id] = p.batting_order
        position_map[p.player_id] = p.position
    
    # Save lineup directly in transaction
    with transaction.atomic():
        User = get_user_model()
        created_by = User.objects.get(pk=created_by_id)
        
        lineup = Lineup.objects.create(
            team=team_obj,
            name=lineup_name,
            created_by=created_by,
        )
        
        # Create LineupPlayer entries with provided batting orders
        lineup_players = []
        for player in players_list:
            position = position_map.get(player.id, player.position)
            batting_order = batting_orders.get(player.id)
            
            lineup_player = LineupPlayer.objects.create(
                lineup=lineup,
                player=player,
                position=position,
                batting_order=batting_order,
            )
            lineup_players.append(lineup_player)
    
    # Validate the produced Lineup model
    validate_lineup_model(lineup)
    
    return lineup, lineup_players


def generate_suggested_lineup(team_id: int) -> list:
    """Generate a suggested lineup using the algorithm WITHOUT saving to database.
    
    Args:
        team_id: The team ID to generate lineup for
        
    Returns:
        List of player dictionaries with suggested batting orders
    """
    from .algorithm_logic import calculate_spot_scores
    
    # Load all players for the team
    players_qs = list(RosterPlayer.objects.filter(team_id=team_id))
    
    # Run algorithm logic to get batting order WITHOUT saving
    available_indices = set(range(len(players_qs)))
    assignments = {}  # batting_order -> player_index
    
    for spot in range(1, 10):  # Spots 1 through 9
        scores = calculate_spot_scores(players_qs, spot)
        best_idx = None
        best_score = -float("inf") if spot != 9 else float("inf")
        
        for idx in available_indices:
            if spot == 9:
                if scores[idx] < best_score:
                    best_score = scores[idx]
                    best_idx = idx
            else:
                if scores[idx] > best_score:
                    best_score = scores[idx]
                    best_idx = idx
        
        if best_idx is not None:
            assignments[spot] = best_idx
            available_indices.remove(best_idx)
    
    # Build response with suggested lineup
    suggested_players = []
    for batting_order, player_idx in sorted(assignments.items()):
        player = players_qs[player_idx]
        suggested_players.append(
            {
                "player_id": player.id,
                "player_name": player.name,
                "position": player.position or "DH",
                "batting_order": batting_order,
            }
        )
    
    return suggested_players

