##########################################
"""contracts/lineups_contract.py
-This file defines the API "contract" for saving a lineup:
- Request schema (what the frontend sends)
- Response schema (what the backend returns)
- Example payloads
- It does NOT create models or endpoints."""
###########################################

from rest_framework import serializers

# ---- Request schema (client -> server) ----
class LineupPlayerIn(serializers.Serializer):
    """This is one batting slot in the lineup."""
    player_id = serializers.IntegerField()
    position = serializers.CharField(max_length=3)    
    batting_order = serializers.IntegerField(min_value=1, max_value=9)


class LineupCreate(serializers.Serializer):
    """This is the entire request body to save a lineup."""
    team_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)            # the coach-entered the name
    opponent_pitcher_id = serializers.IntegerField()
    opponent_team_id = serializers.IntegerField(required=False, allow_null=True)
    players = LineupPlayerIn(many=True, min_length=9, max_length=9)  # calls LineupPlayerIn from above


# ---- Response schema (server -> client) ----
class LineupPlayerOut(serializers.Serializer):
    """This is a saved batting slot returned to the client."""
    player_id = serializers.IntegerField()
    position = serializers.CharField(max_length=3)
    batting_order = serializers.IntegerField()


class LineupOut(serializers.Serializer):
    """This is the entire response body returned by the API after saving."""
    id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    name = serializers.CharField()
    opponent_pitcher_id = serializers.IntegerField()
    opponent_team_id = serializers.IntegerField(required=False, allow_null=True)
    players = LineupPlayerOut(many=True)
    created_by = serializers.IntegerField()
    created_at = serializers.DateTimeField()


ROUTE = "/api/v1/lineups/"
METHOD = "POST"

REQUEST_EXAMPLE = {
    "team_id": 42,
    "name": "vs Cole — Oct12",
    "opponent_pitcher_id": 3109,
    "opponent_team_id": 7,
    "game_date": "2025-10-12",
    "players": [
        {"player_id": 11, "position": "SS", "batting_order": 1},
        {"player_id": 22, "position": "CF", "batting_order": 2},
        {"player_id": 33, "position": "RF", "batting_order": 3},
        {"player_id": 44, "position": "1B", "batting_order": 4},
        {"player_id": 55, "position": "3B", "batting_order": 5},
        {"player_id": 66, "position": "2B", "batting_order": 6},
        {"player_id": 77, "position": "LF", "batting_order": 7},
        {"player_id": 88, "position": "C",  "batting_order": 8},
        {"player_id": 99, "position": "DH", "batting_order": 9}
    ]
}

RESPONSE_EXAMPLE = {
    "id": 1234,
    "team_id": 42,
    "name": "vs Cole — Oct12",
    "opponent_pitcher_id": 3109,
    "opponent_team_id": 7,
    "game_date": "2025-10-12",
    "players": [
        {"player_id": 11, "position": "SS", "batting_order": 1},
        {"player_id": 22, "position": "CF", "batting_order": 2},
        {"player_id": 33, "position": "RF", "batting_order": 3},
        {"player_id": 44, "position": "1B", "batting_order": 4},
        {"player_id": 55, "position": "3B", "batting_order": 5},
        {"player_id": 66, "position": "2B", "batting_order": 6},
        {"player_id": 77, "position": "LF", "batting_order": 7},
        {"player_id": 88, "position": "C",  "batting_order": 8},
        {"player_id": 99, "position": "DH", "batting_order": 9}
    ],
    "created_by": 5,
    "created_at": "2025-10-12T14:33:09Z"
}