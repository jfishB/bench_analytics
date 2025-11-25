"""- This file defines the interactor for lineup creation use case
- Imported by:
  - backend/lineups/views.py
"""
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_batting_orders, validate_data
from .services.lineup_creation_handler import handle_lineup_save, generate_suggested_lineup

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

        # Domain validation
        validate_batting_orders(payload.players)
        validated_data = validate_data(payload)
        
        # Persist to database (created_by_id already in validated_data)
        lineup, lineup_players = handle_lineup_save(validated_data)

        return lineup, lineup_players
    


    def generate_suggested_lineup(self, team_id, selected_player_ids=None):
        """
        Use Case: Generate algorithm-based lineup (no save)
        
        Input: Primitive types
        Output: List of suggested players with batting orders
        """
        from .services.exceptions import DomainError
        
        if team_id is None:
            raise DomainError("team_id is required to generate a suggested lineup")
        
        # Call algorithm service
        suggested_players = generate_suggested_lineup(team_id, selected_player_ids)
        
        return suggested_players