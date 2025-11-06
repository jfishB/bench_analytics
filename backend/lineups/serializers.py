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
    name = serializers.CharField(max_length=120)  # the coach-entered the name
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
