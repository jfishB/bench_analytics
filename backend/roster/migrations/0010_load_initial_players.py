"""
Data migration to load initial Blue Jays players from CSV.
This runs automatically when migrations are applied on Render.
"""

import csv
from pathlib import Path

from django.db import migrations


def load_players(apps, schema_editor):
    """Load players from the test dataset CSV file."""
    Player = apps.get_model("roster", "Player")

    # When running on Render, the working directory is the repo root
    # So data/ is accessible directly
    csv_path = Path("data/test_dataset_monte_carlo_bluejays.csv")

    # For local development from backend/ directory
    if not csv_path.exists():
        csv_path = Path("../data/test_dataset_monte_carlo_bluejays.csv")

    if not csv_path.exists():
        print("CSV file not found, skipping player import")
        return

    print(f"Loading players from {csv_path.absolute()}")

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        players_loaded = 0

        for row in reader:
            name = row.get('"last_name, first_name"') or row.get("last_name, first_name")
            if not name or not name.strip():
                continue

            def to_float(val):
                """Convert string value to float, handling quotes and empty values."""
                if not val or val == "":
                    return None
                try:
                    return float(str(val).replace('"', "").replace("%", "").strip())
                except (ValueError, AttributeError):
                    return None

            def to_int(val):
                """Convert string value to int, handling quotes and empty values."""
                if not val or val == "":
                    return None
                try:
                    return int(float(str(val).replace('"', "").strip()))
                except (ValueError, AttributeError):
                    return None

            Player.objects.update_or_create(
                name=name.strip(),
                defaults={
                    "year": to_int(row.get("year")),
                    "pa": to_int(row.get("pa")),
                    "hit": to_int(row.get("hit")),
                    "double": to_int(row.get("double")),
                    "triple": to_int(row.get("triple")),
                    "home_run": to_int(row.get("home_run")),
                    "strikeout": to_int(row.get("strikeout")),
                    "walk": to_int(row.get("walk")),
                    "k_percent": to_float(row.get("k_percent")),
                    "bb_percent": to_float(row.get("bb_percent")),
                    "slg_percent": to_float(row.get("slg_percent")),
                    "on_base_percent": to_float(row.get("on_base_percent")),
                    "isolated_power": to_float(row.get("isolated_power")),
                    "r_total_stolen_base": to_float(row.get("r_total_stolen_base")),
                },
            )
            players_loaded += 1

    count = Player.objects.count()
    print(f"Successfully loaded {players_loaded} players. Total players in database: {count}")


def reverse_players(apps, schema_editor):
    """Optional: Clean up players if migration is reversed."""
    # We'll leave players in place even if migration is reversed
    # to avoid accidental data loss
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("roster", "0009_remove_player_position"),
    ]

    operations = [
        migrations.RunPython(load_players, reverse_players),
    ]


