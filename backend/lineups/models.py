from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from roster.models import Team, Player


class Lineup(models.Model):  # each instance is a saved batting lineup for a team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")
    name = models.CharField(max_length=120)  # coach-entered name for the lineup
    opponent_pitcher = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="+")

    opponent_team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lineups"
        ordering = ["-created_at", "name"]  # newest first, then name

    def __str__(self):
        when = self.created_at.date().isoformat()
        return f"{self.team.name} — {self.name} ({when})"
  
class LineupPlayer(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    position = models.CharField(max_length=3)
    batting_order = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(9)]
    )

    class Meta:
        db_table = "lineup_players"
        ordering = ["batting_order"]  # 1..9 by default
        constraints = [
            models.UniqueConstraint(fields=["lineup", "player"], name="unique_player_per_lineup"),
            models.UniqueConstraint(fields=["lineup", "batting_order"], name="unique_batting_order_per_lineup"),
        ]

    def __str__(self):
        return f"{self.batting_order}. {self.player.name} ({self.position})"
