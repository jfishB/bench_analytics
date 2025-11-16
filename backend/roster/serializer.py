from rest_framework import serializers

from .models import Player, Team


class PlayerNameValidationMixin:
    """Mixin to provide shared player name validation."""

    def validate_name(self, value: str) -> str:
        """Ensure player name is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Player name cannot be empty.")
        return value.strip()


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""

    class Meta:
        model = Team
        fields = "__all__"


class PlayerSerializer(PlayerNameValidationMixin, serializers.ModelSerializer):
    """Serializer for Player model with nested team information."""

    class Meta:
        model = Player
        fields = [
            "name",
            "player_id",
            "team",
            "position",
            "year",
            "ab",
            "pa",
            "hit",
            "single",
            "double",
            "triple",
            "home_run",
            "walk",
            "k_percent",
            "bb_percent",
            "slg_percent",
            "on_base_percent",
            "isolated_power",
            "b_total_bases",
            "r_total_caught_stealing",
            "r_total_stolen_base",
            "b_game",
            "b_gnd_into_dp",
            "b_hit_by_pitch",
            "b_intent_walk",
            "b_sac_fly",
            "b_total_sacrifices",
            "woba",
            "xwoba",
            "barrel_batted_rate",
            "hard_hit_percent",
            "sprint_speed",
        ]


class PlayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing players."""

    class Meta:
        model = Player
        fields = ["id", "name", "team", "position"]


class PlayerRankedSerializer(PlayerSerializer):
    """Serializer for ranked players with WOS score."""

    wos_score = serializers.FloatField(read_only=True)

    class Meta(PlayerSerializer.Meta):
        fields = [
            "id",
            "name",
            "team",
            "position",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "wos_score",
        ]


class PlayerCreateSerializer(PlayerNameValidationMixin, serializers.ModelSerializer):
    """Serializer for creating a new player with validation."""

    class Meta:
        model = Player
        fields = [
            "name",
            "player_id",
            "team",
            "position",
            "year",
            "ab",
            "pa",
            "hit",
            "single",
            "double",
            "triple",
            "home_run",
            "walk",
            "k_percent",
            "bb_percent",
            "slg_percent",
            "on_base_percent",
            "isolated_power",
            "b_total_bases",
            "r_total_caught_stealing",
            "r_total_stolen_base",
            "b_game",
            "b_gnd_into_dp",
            "b_hit_by_pitch",
            "b_intent_walk",
            "b_sac_fly",
            "b_total_sacrifices",
            "woba",
            "xwoba",
            "barrel_batted_rate",
            "hard_hit_percent",
            "sprint_speed",
        ]


class PlayerPartialUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partially updating player stats."""

    class Meta:
        model = Player
        fields = [
            "name",
            "player_id",
            "team",
            "position",
            "year",
            "ab",
            "pa",
            "hit",
            "single",
            "double",
            "triple",
            "home_run",
            "walk",
            "k_percent",
            "bb_percent",
            "slg_percent",
            "on_base_percent",
            "isolated_power",
            "b_total_bases",
            "r_total_caught_stealing",
            "r_total_stolen_base",
            "b_game",
            "b_gnd_into_dp",
            "b_hit_by_pitch",
            "b_intent_walk",
            "b_sac_fly",
            "b_total_sacrifices",
            "woba",
            "xwoba",
            "barrel_batted_rate",
            "hard_hit_percent",
            "sprint_speed",
        ]
        extra_kwargs = {
            "name": {"required": False},
            "team": {"required": False},
            "position": {"required": False},
        }

    def validate_name(self, value: str) -> str:
        """Ensure player name is not empty after stripping whitespace."""
        if value and not value.strip():
            raise serializers.ValidationError("Player name cannot be empty.")
        return value.strip() if value else value


class PlayerRankQuerySerializer(serializers.Serializer):
    """Serializer for validating query parameters for ranked endpoint."""

    ascending = serializers.BooleanField(default=False, required=False)
    top = serializers.IntegerField(min_value=1, required=False)
