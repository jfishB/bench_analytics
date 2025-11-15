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
    batting_order = serializers.IntegerField(
        min_value=1, max_value=9, required=False, allow_null=True
    )


class LineupCreate(serializers.Serializer):
    """This is the entire request body to save a lineup."""

    team_id = serializers.IntegerField()
    players = LineupPlayerIn(
        many=True, min_length=9, max_length=9
    )  # calls LineupPlayerIn from above
    name = serializers.CharField(max_length=120, required=False, allow_blank=False)


class LineupCreateByTeam(serializers.Serializer):
    """Create lineup request containing only a team identifier.

    The frontend may supply only a team_id (and optional metadata). The
    server will load players for that team and run the algorithm.
    """

    team_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120, required=False, allow_blank=False)


# ---- Response schema (server -> client) ----
class LineupPlayerOut(serializers.Serializer):
    """This is a saved batting slot returned to the client."""

    player_id = serializers.IntegerField()
    # Use a SerializerMethodField so the serializer works whether the
    # input is a dict (views build a dict with 'player_name') or a
    # LineupPlayer model instance. This avoids KeyError during
    # representation when the nested instance doesn't have a
    # `player_name` attribute/key.
    player_name = serializers.SerializerMethodField()
    position = serializers.CharField(max_length=3)
    batting_order = serializers.IntegerField()

    def get_player_name(self, obj):
        # If the serializer was given a dict (as in our view builders),
        # return the explicit 'player_name' key if present.
        if isinstance(obj, dict):
            # obj may be like {"player_id": 1, "player_name": "Foo", ...}
            # prefer explicit 'player_name' key that views set, fall back to 'name'
            return obj.get("player_name") or obj.get("name")

        # Otherwise assume obj is a LineupPlayer model instance and
        # try to read the related player's name. Be defensive in case
        # the relation is missing.
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

    players = serializers.SerializerMethodField()

    class Meta:
        from .models import Lineup

        model = Lineup
        fields = ["id", "team_id", "name", "created_by", "created_at", "players"]
        read_only_fields = ["id", "created_at"]

    def get_players(self, obj):
        """Return the lineup players in batting order."""
        lineup_players = obj.players.order_by("batting_order")
        return [
            {
                "player_id": lp.player_id,
                "player_name": lp.player.name if lp.player else None,
                "position": lp.position,
                "batting_order": lp.batting_order,
            }
            for lp in lineup_players
        ]
