##########################################
"""
-This file defines the API "contract"
for saving a lineup
-used in lineup services and validation.
"""
###########################################

from rest_framework import serializers


# ---- Request schema (client -> server) ----
class LineupPlayerIn(serializers.Serializer):
    """This is one batting slot in the lineup."""

    player_id = serializers.IntegerField()
    position = serializers.CharField(max_length=3)
    # bating order is optional because the algorithm may assign it
    batting_order = serializers.IntegerField(min_value=1, max_value=9, required=False, allow_null=True)


class LineupCreate(serializers.Serializer):
    """This is the entire request body to save a lineup."""

    team_id = serializers.IntegerField()
    players = LineupPlayerIn(many=True, min_length=9, max_length=9)  # calls LineupPlayerIn from above


class LineupCreateByTeam(serializers.Serializer):
    """Create lineup request containing only a team identifier.

    The frontend may supply only a team_id (and optional metadata). The
    server will load players for that team and run the algorithm.
    """

    team_id = serializers.IntegerField()

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
    players = LineupPlayerOut(many=True)
    created_by = serializers.IntegerField()
    created_at = serializers.DateTimeField()
