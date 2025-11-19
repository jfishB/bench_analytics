from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from roster.models import Player, Team


class Lineup(models.Model):  # each instance is a saved batting lineup for a team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")
    name = models.CharField(max_length=120)  # coach-entered name for the lineup
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lineups"
        ordering = ["-created_at", "name"]  # newest first, then name

    def __str__(self):
        when = self.created_at.date().isoformat()
        # Team no longer has a name field; display using team id instead.
        return f"Team {self.team_id} — {self.name} ({when})"


class LineupPlayer(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    batting_order = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(9)]
    )

    class Meta:
        db_table = "lineup_players"
        ordering = ["batting_order"]  # 1..9 by default
        constraints = [
            models.UniqueConstraint(fields=["lineup", "player"], name="unique_player_per_lineup"),
            models.UniqueConstraint(
                fields=["lineup", "batting_order"],
                name="unique_batting_order_per_lineup",
            ),
        ]

    def __str__(self):
        return f"{self.batting_order}. {self.player.name}"
