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

    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "team",
            "team_name",
            "position",
            "woba",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "on_base_percent",
            "slg_percent",
            "sprint_speed",
            "r_total_stolen_base",
            "isolated_power",
            "hard_hit_percent",
            "home_run",
            "pa",
            "year",
        ]


class PlayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing players."""

    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Player
        fields = ["id", "name", "team", "team_name", "position"]


class PlayerRankedSerializer(PlayerSerializer):
    """Serializer for ranked players with WOS score."""

    wos_score = serializers.FloatField(read_only=True)

    class Meta(PlayerSerializer.Meta):
        fields = [
            "id",
            "name",
            "team",
            "team_name",
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
            "team",
            "position",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "pa",
            "year",
            "savant_player_id",
            "sweet_spot_percent",
            "hard_hit_percent",
            "avg_best_speed",
            "avg_hyper_speed",
            "whiff_percent",
            "swing_percent",
            "woba",
        ]


class PlayerPartialUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partially updating player stats."""

    class Meta:
        model = Player
        fields = [
            "name",
            "team",
            "position",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "pa",
            "year",
            "savant_player_id",
            "sweet_spot_percent",
            "hard_hit_percent",
            "avg_best_speed",
            "avg_hyper_speed",
            "whiff_percent",
            "swing_percent",
            "woba",
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
