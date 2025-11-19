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
    ab = models.PositiveIntegerField(null=True, blank=True)  # At bat count
    pa = models.PositiveIntegerField(null=True, blank=True)  # Plate appearances
    hit = models.PositiveIntegerField(null=True, blank=True)  # Total hits
    single = models.PositiveIntegerField(null=True, blank=True)  # Singles
    double = models.PositiveIntegerField(null=True, blank=True)  # Doubles
    triple = models.PositiveIntegerField(null=True, blank=True)  # Triples
    home_run = models.PositiveIntegerField(null=True, blank=True)  # Home runs
    strikeout = models.PositiveIntegerField(null=True, blank=True)  # Strikeouts
    walk = models.PositiveIntegerField(null=True, blank=True)  # Walks - BB
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
    b_total_bases = models.FloatField(
        null=True, blank=True
    )  # TB: Total bases - 1 x Singles + 2 x Doubles + 3 x Triples + 4 x Home Runs
    r_total_caught_stealing = models.FloatField(
        null=True, blank=True
    )  # CS: Caught Stealing - When a runner is put out by the defense while attempting to steal a base
    r_total_stolen_base = models.FloatField(
        null=True, blank=True
    )  # SB: Stolen bases - Count of successful stolen base attempts
    b_game = models.FloatField(null=True, blank=True)  # G: Games played - Total games played in a season
    b_gnd_into_dp = models.FloatField(
        null=True, blank=True
    )  # GIPD: Grounded Into Double Play - Counts the times a batter hits a ground ball that results in two outs in one continuous play
    b_hit_by_pitch = models.FloatField(
        null=True, blank=True
    )  # HPB: A hit-by-pitch occurs when a batter is struck by a pitched ball without swinging at it.
    b_intent_walk = models.FloatField(
        null=True, blank=True
    )  # IBB: Intentional Base on Balls / Intentional walk - A strategic play where the defending team deliberately allows a batter to reach first base without having to swing at a pitch.
    b_sac_bunt = models.FloatField(
        null=True, blank=True
    )  # SH: Sacrfice bunt: Occurs when a batter deliberately bunts the ball to advance a baserunner, usually at the cost of being put out themselves
    b_sac_fly = models.FloatField(
        null=True, blank=True
    )  # SF: Sacrifice Fly - Occurs when a batter hits a deep fly ball that is caught by an outfielder (or an infielder playing in the outfield), but a baserunner on third base tags up and scores before the play is over.

    class Meta:
        db_table = "players"
        ordering = ["name"]  # alphabetical order

    def __str__(self):
        return f"{self.name} ({self.position})"
