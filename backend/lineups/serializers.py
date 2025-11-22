##########################################
"""
-This file defines the API "contract"
for saving a lineup
-used in lineup services and validation.
"""
###########################################

from rest_framework import serializers

from .models import Lineup


# ---- Request schema (client -> server) ----
class LineupPlayerIn(serializers.Serializer):
    """This is one batting slot in the lineup."""

    player_id = serializers.IntegerField()
    # bating order is optional because the algorithm may assign it
    batting_order = serializers.IntegerField(min_value=1, max_value=9, required=False, allow_null=True)



class LineupCreate(serializers.Serializer):
    """This is the entire request body to save a lineup."""

    team_id = serializers.IntegerField()
    players = LineupPlayerIn(many=True, min_length=9, max_length=9)  # calls LineupPlayerIn from above
    name = serializers.CharField(max_length=120, required=False, allow_blank=False)


# ---- Response schema (server -> client) ----
class LineupPlayerOut(serializers.Serializer):
    """This is a saved batting slot returned to the client."""

    player_id = serializers.IntegerField()
    player_name = serializers.SerializerMethodField()
    batting_order = serializers.IntegerField()

    def get_player_name(self, obj):
        """Return the player's name."""
        try:
            return obj.player.name
        except Exception:
            return None


class LineupOut(serializers.Serializer):
    """This is the entire response body returned by the API after saving."""

    id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)
    players = LineupPlayerOut(many=True)
    created_by = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class LineupModelSerializer(serializers.ModelSerializer):
    """ModelSerializer for Lineup - used by ViewSet for list/retrieve operations."""

    created_by = serializers.ReadOnlyField(source="created_by_id")
    players = serializers.SerializerMethodField()

    class Meta:
        model = Lineup
        fields = ["id", "team_id", "name", "created_by", "created_at", "players"]
        read_only_fields = ["id", "created_at"]

    def get_players(self, obj):
        """Return the lineup players in batting order.

        Filters out players with None batting_order to handle incomplete lineups.
        """
        lineup_players = obj.players.order_by("batting_order")
        return [
            {
                "player_id": lp.player_id,
                "player_name": lp.player.name if lp.player else None,
                "batting_order": lp.batting_order,
            }
            for lp in lineup_players
            if lp.batting_order is not None  # Filter out None batting orders
        ]
