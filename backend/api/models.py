"""
Models for the lineup feature.
Inclues: 
- Team:            A baseball team 
- Player:          A rostered player belonging to a Team (with a short position code).
- Lineup:          A saved batting lineup for a Team, optionally tied to an opponent pitcher/team/date.
- LineupPlayer:    One batting slot (1–9) in a Lineup linking to a specific Player,
                   storing the position snapshot and batting_order.

Key relationships & delete behavior:
- Player.team -> CASCADE: deleting a Team deletes its Players.
- Lineup.team -> CASCADE: deleting a Team deletes its Lineups (and their LineupPlayers).
- LineupPlayer.lineup -> CASCADE: deleting a Lineup deletes its LineupPlayers.
- Lineup.opponent_pitcher / LineupPlayer.player -> PROTECT: prevents deleting Players
  that are referenced in saved lineups, preserving historical integrity.

Schema note:
- We rely on PostgreSQL `search_path` (e.g., "app,public") to decide which schema
  tables are created in. Do NOT prefix schema names in db_table.

Conventions:
- db_table is set explicitly for readability ("teams", "players", "lineups", "lineup_players").
- Default ordering:
  - Team/Player by name,
  - Lineup newest first (created_at desc),
  - LineupPlayer by batting_order (1..9).

Typical queries:
- team.players.all()                         # all players on a team
- team.lineups.order_by("-created_at")       # a team’s saved lineups, newest first
- lineup.players.all()                       # batting order (1..9) for a lineup
- Player.objects.filter(team=team, position="SS")

These models are used by the API endpoint that saves a lineup. The endpoint:
1) validates the request via DRF serializers (the “contract”),
2) creates a Lineup and its 9 LineupPlayer rows in a transaction,
3) returns a standardized JSON response for the frontend.
"""

from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = "teams"
        ordering = ["name"]   # alphabetical order              

    def __str__(self):
        return self.name


class Player(models.Model):
    """Basic player model storing player information."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", default=1)
    position = models.CharField(max_length=3, default="DH")  # e.g., SS/CF/DH

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name} ({self.position})"

class Lineup(models.Model):  # each instance is a saved batting lineup for a team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")  # the team this lineup is for last part is 
    # is for reverse lookup, e.g. team.lineups.all()
    name = models.CharField(max_length=120) # coach-entered name for the lineup
    opponent_pitcher = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="+")  # the opposing pitcher protected from deletion if referenced in a lineup
    # related_name="+" means no reverse relation from opponent_pitcher to Lineup
    opponent_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lineups"
        ordering = ["-created_at", "name"]  # newest first, then name

    def __str__(self):
        when = self.game_date.isoformat() if self.game_date else self.created_at.date().isoformat()
        return f"{self.team.name} — {self.name} ({when})"


class LineupPlayer(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    position = models.CharField(max_length=3)            
    batting_order = models.PositiveSmallIntegerField()    

    class Meta:
        db_table = "lineup_players"
        ordering = ["batting_order"]        # 1..9 by default

    def __str__(self):
        return f"{self.batting_order}. {self.player.name} ({self.position})"
    
class Login(models.Model):
    """
    Stores login-related information for users.
    This table tracks login credentials and metadata but does not replace Django’s built-in User model.
    """

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "logins"
        ordering = ["username"]

    def __str__(self):
        return self.username