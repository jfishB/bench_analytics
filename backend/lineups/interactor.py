"""
-This file defines the interactor for lineup creation use case
-Imported by:
  -backend/lineups/views.py
"""
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_batting_orders, validate_data
from .services.databa_access import fetch_lineup_data
from .services.lineup_creation_handler import handle_lineup_save
from .services.exceptions import DomainError
from .services.algorithm_logic import algorithm_create_lineup
        

class LineupCreationInteractor:
    """Organizes the complete lineup creation use case"""
    
    def create_manual_lineup(self, team_id, players_data, user_id, name=None):
        """
        Use Case: Create and save a manual lineup
        
        Input: Primitive types (int, list of dicts, str)
        Output: Domain result (lineup + players) or raises DomainError
        """

        players_input = [
            LineupPlayerInput(
                player_id=p["player_id"],
                batting_order=p.get("batting_order"),
            )
            for p in players_data
        ]

        payload = CreateLineupInput(
            team_id=team_id,
            players=players_input,
            requested_user_id=user_id,
            name=name,
        )

        # Domain validation (raises exceptions if invalid)
        validate_batting_orders(payload.players)
        validate_data(payload, require_creator=True)
        
        # Fetch data from database
        lineup_data = fetch_lineup_data(payload)
        original_batting_orders = [p.batting_order for p in payload.players]
        
        # Persist to database
        lineup, lineup_players = handle_lineup_save(lineup_data, original_batting_orders)

        return lineup, lineup_players
    


    def generate_suggested_lineup(self, team_id, selected_player_ids=None):
        """
        Use Case: Generate algorithm-based lineup (no save)
        
        Input: Primitive types
        Output: List of suggested players with batting orders
        """

        if team_id is None:
            raise DomainError("team_id is required to generate a suggested lineup")
        
        # Build payload - limit to 9 players
        if selected_player_ids:
            players_inputs = [LineupPlayerInput(player_id=pid) for pid in selected_player_ids][:9]
        else:
            raise DomainError("Player IDs are required to generate a suggested lineup")
        
        payload = CreateLineupInput(team_id=team_id, players=players_inputs, requested_user_id=None)
        
        # Validate and fetch data from database
        validate_data(payload, require_creator=False)
        validated_data = fetch_lineup_data(payload)
        
        # Call algorithm with fetched players
        lineup_tuple = algorithm_create_lineup(validated_data["players"])
        
        if not lineup_tuple:
            return [] 
        
        # Format result
        suggested_players = [
            {
                "player_id": p.id,
                "player_name": getattr(p, "name", ""),
                "batting_order": idx + 1,
            }
            for idx, p in enumerate(lineup_tuple)
        ]
        
        return suggested_players