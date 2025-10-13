from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Player(models.Model):
    """Basic player model storing player information."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=3)  # e.g., SS/CF/DH

    class Meta:
        db_table = "players"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lineup(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")
    name = models.CharField(max_length=120)
    opponent_pitcher = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="+")
    opponent_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

class LineupPlayer(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    position = models.CharField(max_length=3)            
    batting_order = models.PositiveSmallIntegerField()    