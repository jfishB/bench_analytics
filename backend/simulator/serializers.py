"""
serializers for validating api request inputs and formatting response outputs.
uses django rest framework serializers to enforce constraints like 9 players required,
game count limits (100-100k), and structure simulation results consistently.
called by views.py for all three endpoints (by ids, names, team).
"""

from rest_framework import serializers


class PlayerInputSerializer(serializers.Serializer):
    """Input serializer for specifying players by ID."""

    player_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=9,
        max_length=9,
        help_text="List of exactly 9 player IDs in batting order",
    )
    num_games = serializers.IntegerField(
        default=10000, min_value=100, max_value=100000, help_text="Number of games to simulate"
    )


class PlayerNameInputSerializer(serializers.Serializer):
    """Input serializer for specifying players by name."""

    player_names = serializers.ListField(
        child=serializers.CharField(),
        min_length=9,
        max_length=9,
        help_text="List of exactly 9 player names in batting order",
    )
    num_games = serializers.IntegerField(
        default=10000, min_value=100, max_value=100000, help_text="Number of games to simulate"
    )


class TeamInputSerializer(serializers.Serializer):
    """Input serializer for using a team's top players."""

    team_id = serializers.IntegerField(help_text="Team ID to use")
    num_games = serializers.IntegerField(
        default=10000, min_value=100, max_value=100000, help_text="Number of games to simulate"
    )


class SimulationResultSerializer(serializers.Serializer):
    """Output serializer for simulation results."""

    lineup = serializers.ListField(child=serializers.CharField(), help_text="Player names in batting order")
    num_games = serializers.IntegerField()
    avg_score = serializers.FloatField()
    median_score = serializers.FloatField()
    std_dev = serializers.FloatField()
    min_score = serializers.IntegerField()
    max_score = serializers.IntegerField()
    score_distribution = serializers.DictField(child=serializers.IntegerField(), help_text="Mapping of score -> frequency")
