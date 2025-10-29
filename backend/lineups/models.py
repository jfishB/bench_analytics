from django.db import models
from django.conf import settings
from roster.models import Team, Player
    
class Lineup(models.Model):  # each instance is a saved batting lineup for a team
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="lineups"
    )  # the team this lineup is for last part is
    # is for reverse lookup, e.g. team.lineups.all()
    name = models.CharField(max_length=120)  # coach-entered name for the lineup
    opponent_pitcher = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="+"
    )  # the opposing pitcher protected from deletion if referenced in a lineup
    # related_name="+" means no reverse relation from opponent_pitcher to Lineup
    opponent_team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lineups"
        ordering = ["-created_at", "name"]  # newest first, then name

    def __str__(self):
        when = (
            self.game_date.isoformat()
            if self.game_date
            else self.created_at.date().isoformat()
        )
        return f"{self.team.name} — {self.name} ({when})"
  
class LineupPlayer(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    position = models.CharField(max_length=3)
    batting_order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "lineup_players"
        ordering = ["batting_order"]  # 1..9 by default

    def __str__(self):
        return f"{self.batting_order}. {self.player.name} ({self.position})"
