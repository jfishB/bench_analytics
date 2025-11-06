from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "teams"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return self.name


class Player(models.Model):
    """Basic player model storing player information."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", null=True, blank=True)
    position = models.CharField(max_length=3, default="DH")  # e.g., SS/CF/DH

    # Baseball Savant (2025) batter stats snapshot — optional, filled via CSV import
    # Note: These are per-season aggregates; if you later want multi-year history,
    # consider a separate PlayerSeasonStats model instead of widening Player.
    savant_player_id = models.PositiveIntegerField(null=True, blank=True)  # external player_id
    year = models.PositiveIntegerField(null=True, blank=True)  # season year (e.g., 2025)
    pa = models.PositiveIntegerField(null=True, blank=True)  # plate appearances
    k_percent = models.FloatField(null=True, blank=True)  # strikeout %
    bb_percent = models.FloatField(null=True, blank=True)  # walk %
    woba = models.FloatField(null=True, blank=True)  # weighted on-base average
    xwoba = models.FloatField(null=True, blank=True)  # expected wOBA
    sweet_spot_percent = models.FloatField(null=True, blank=True)
    barrel_batted_rate = models.FloatField(null=True, blank=True)
    hard_hit_percent = models.FloatField(null=True, blank=True)
    avg_best_speed = models.FloatField(null=True, blank=True)  # mph
    avg_hyper_speed = models.FloatField(null=True, blank=True)  # mph
    whiff_percent = models.FloatField(null=True, blank=True)
    swing_percent = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name} ({self.position})"
