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

    # Baseball Savant (2025) batter stats snapshot
    # Note: These are per-season aggregates; if you later want multi-year history,
    # Stat explanations from: https://baseballsavant.mlb.com/leaderboard/custom?year=2025&type=batter&filter=&min=q&selections=pa%2Chome_run%2Ck_percent%2Cbb_percent%2Cslg_percent%2Con_base_percent%2Cisolated_power%2Cr_total_stolen_base%2Cwoba%2Cxwoba%2Cbarrel_batted_rate%2Chard_hit_percent%2Csprint_speed&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=1&sortDir=desc
    savant_player_id = models.PositiveIntegerField(null=True, blank=True)  # External player_id
    year = models.PositiveIntegerField(null=True, blank=True)  # Season year (e.g., 2025)
    pa = models.PositiveIntegerField(null=True, blank=True)  # Plate appearances
    home_run = models.FloatField(null=True, blank=True)  # Home run rate
    k_percent = models.FloatField(null=True, blank=True)  # Strikeout %
    bb_percent = models.FloatField(null=True, blank=True)  # Walk %
    slg_percent = models.FloatField(null=True, blank=True)  # Slugging percentage
    on_base_percent = models.FloatField(null=True, blank=True)  # On-base percentage
    isolated_power = models.FloatField(null=True, blank=True)  # Isolated power (SLG − AVG)
    r_total_stolen_base = models.FloatField(null=True, blank=True)  # Stolen bases
    woba = models.FloatField(null=True, blank=True)  # weighted on-base average
    xwoba = models.FloatField(null=True, blank=True)  # expected xwOBA: formulated using exit velocity, launch angle and, on certain types of batted balls, Sprint Speed.
    barrel_batted_rate = models.FloatField(null=True, blank=True) # A batted ball with the perfect combination of exit velocity and launch angle
    hard_hit_percent = models.FloatField(null=True, blank=True) # Statcast defines a 'hard-hit ball' as one hit with an exit velocity of 95 mph or higher.
    sprint_speed = models.FloatField(null=True, blank=True) # A measurement of a player's top running speed, expressed in "feet per second in a player's fastest one-second window."

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name} ({self.position})"
