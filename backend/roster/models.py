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
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", null=True, blank=True)
    position = models.CharField(max_length=3, default="DH")  # e.g., SS/CF/DH

    # Baseball Savant (2025) batter stats snapshot
    # Note: These are per-season aggregates; if you later want multi-year history,
    # Stat explanations from: https://baseballsavant.mlb.com/leaderboard/custom?year=2025&type=batter&filter=&min=q&selections=pa%2Chome_run%2Ck_percent%2Cbb_percent%2Cslg_percent%2Con_base_percent%2Cisolated_power%2Cr_total_stolen_base%2Cwoba%2Cxwoba%2Cbarrel_batted_rate%2Chard_hit_percent%2Csprint_speed&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=1&sortDir=desc
    savant_player_id = models.PositiveIntegerField(null=True, blank=True)  # External player_id
    year = models.PositiveIntegerField(null=True, blank=True)  # Season year (e.g., 2025)
    pa = models.PositiveIntegerField(null=True, blank=True)  # Plate appearances
    home_run = models.FloatField(null=True, blank=True)  # Home run rate - HR per PA
    k_percent = models.FloatField(null=True, blank=True)  # Frequency of strikeouts per plate appearance - K% = (SO / PA) * 100
    bb_percent = models.FloatField(null=True, blank=True)  # Frequency of walks per plate appearance - BB% = (BB / PA) * 100
    slg_percent = models.FloatField(
        null=True, blank=True
    )  # Measures total bases per at-bat, emphasizes extra-base hits - SLG = (1B + 2*2B + 3*3B + 4*HR) / AB
    on_base_percent = models.FloatField(
        null=True, blank=True
    )  # On-base percentage: Measures how often a batter reaches base safely - OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
    isolated_power = models.FloatField(
        null=True, blank=True
    )  # Shows extra bases per at-bat (pure power) - ISO = SLG - AVG | (AVG = H / AB)
    r_total_stolen_base = models.FloatField(null=True, blank=True)  # Stolen bases - Count of successful stolen base attempts
    woba = models.FloatField(
        null=True, blank=True
    )  # Weighted On-Base Average: Weights each event by its average run value (Weights vary slightly each season) - wOBA = ((0.69*uBB) + (0.72*HBP) + (0.89*1B) + (1.27*2B) + (1.62*3B) + (2.10*HR)) / (AB + BB - IBB + SF + HBP)
    xwoba = models.FloatField(
        null=True, blank=True
    )  # Expected wOBA: Derived from Statcast models; estimates what wOBA should be based on contact quality - xwOBA = Expected value based on exit velocity, launch angle, and sprint speed
    barrel_batted_rate = models.FloatField(
        null=True, blank=True
    )  # A "barrel" is a batted ball with optimal exit velocity and launch angle (typically >= 98 mph exit velocity and ~26–30° launch angle) - Barrel% = (Barreled Balls / Batted Balls) * 100
    hard_hit_percent = models.FloatField(
        null=True, blank=True
    )  # Shows how often a player hits the ball hard - HardHit% = (Batted Balls ≥ 95 mph) / (Total Batted Balls) * 100
    sprint_speed = models.FloatField(
        null=True, blank=True
    )  # Average feet per second during top 1-second window of a player's max-effort runs - MLB average ≈ 27 ft/sec; elite ≈ 30+ ft/sec

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name} ({self.position})"
