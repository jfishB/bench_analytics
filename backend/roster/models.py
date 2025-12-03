from django.db import models


class Team(models.Model):
    # Name removed by design — teams are identified by id only.

    class Meta:
        db_table = "teams"
        ordering = ["id"]

    def __str__(self):
        return f"Team {self.id}"


class Player(models.Model):
    """Basic player model storing player information."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="players",
        null=True,
        blank=True,
    )

    # Baseball Savant (2025) batter stats snapshot
    # Note: These are per-season aggregates
    savant_player_id = models.PositiveIntegerField(
        null=True, blank=True)  # External player_id
    year = models.PositiveIntegerField(
        null=True, blank=True)  # Season year (e.g., 2025)
    ab = models.PositiveIntegerField(null=True, blank=True)  # At bat count
    pa = models.PositiveIntegerField(
        null=True, blank=True)  # Plate appearances
    hit = models.PositiveIntegerField(null=True, blank=True)  # Total hits
    single = models.PositiveIntegerField(null=True, blank=True)  # Singles
    double = models.PositiveIntegerField(null=True, blank=True)  # Doubles
    triple = models.PositiveIntegerField(null=True, blank=True)  # Triples
    home_run = models.PositiveIntegerField(null=True, blank=True)  # Home runs
    strikeout = models.PositiveIntegerField(
        null=True, blank=True)  # Strikeouts
    walk = models.PositiveIntegerField(null=True, blank=True)  # Walks - BB
    # K%: Frequency of strikeouts per plate appearance
    k_percent = models.FloatField(null=True, blank=True)
    # BB%: Frequency of walks per plate appearance
    bb_percent = models.FloatField(null=True, blank=True)
    # SLG: Slugging percentage - total bases per at-bat
    slg_percent = models.FloatField(null=True, blank=True)
    # OBP: On-base percentage - how often batter reaches base
    on_base_percent = models.FloatField(null=True, blank=True)
    # ISO: Isolated power - extra bases per at-bat (pure power)
    isolated_power = models.FloatField(null=True, blank=True)
    # TB: Total bases
    b_total_bases = models.FloatField(null=True, blank=True)
    # CS: Caught Stealing
    r_total_caught_stealing = models.FloatField(null=True, blank=True)
    # SB: Stolen bases
    r_total_stolen_base = models.FloatField(null=True, blank=True)
    # G: Games played
    b_game = models.FloatField(null=True, blank=True)
    # GIDP: Grounded Into Double Play
    b_gnd_into_dp = models.FloatField(null=True, blank=True)
    # HBP: Hit by pitch
    b_hit_by_pitch = models.FloatField(null=True, blank=True)
    # IBB: Intentional walk
    b_intent_walk = models.FloatField(null=True, blank=True)
    # SH: Sacrifice bunt
    b_sac_bunt = models.FloatField(null=True, blank=True)
    # SF: Sacrifice fly
    b_sac_fly = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name}"
