"""Service function to import batter stats CSV into the roster Player model.

This was converted from the previous management command to a callable
service function so it can be invoked from code, tests or a lightweight
management wrapper if desired.
"""

import csv
from pathlib import Path
from typing import Tuple

from django.db import transaction

from roster.models import Player


def load_csv_file(
    file: str | Path, year: int | None = None, dry_run: bool = False
) -> Tuple[int, int, int]:
    """Load CSV into roster.Player.

    Returns a tuple (imported, updated, skipped).
    """
    file_path = Path(file)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    imported = 0
    updated = 0
    skipped = 0

    with file_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if dry_run:
        # Caller can print or assert the content as needed
        return (0, 0, len(rows))

    with transaction.atomic():
        for r in rows:
            raw_name = r.get("last_name, first_name")
            if not raw_name:
                skipped += 1
                continue

            name = raw_name.strip()

            player, created = Player.objects.get_or_create(name=name)

            def fflt(key: str):
                v = r.get(key)
                if v is None or v == "":
                    return None
                try:
                    return float(str(v).replace('"', "").replace("%", "").strip())
                except ValueError:
                    return None

            try:
                savant_id = int(r.get("player_id")) if r.get("player_id") else None
            except ValueError:
                savant_id = None

            try:
                pa = int(r.get("pa")) if r.get("pa") else None
            except ValueError:
                pa = None

            row_year = int(r.get("year")) if r.get("year") else None
            use_year = year if year is not None else row_year

            player.savant_player_id = savant_id
            player.year = use_year
            player.pa = pa
            player.home_run = fflt("home_run")
            player.k_percent = fflt("k_percent")
            player.bb_percent = fflt("bb_percent")
            player.slg_percent = fflt("slg_percent")
            player.on_base_percent = fflt("on_base_percent")
            player.isolated_power = fflt("isolated_power")
            player.r_total_stolen_base = fflt("r_total_stolen_base")
            player.woba = fflt("woba")
            player.xwoba = fflt("xwoba")
            player.barrel_batted_rate = fflt("barrel_batted_rate")
            player.hard_hit_percent = fflt("hard_hit_percent")
            player.sprint_speed = fflt("sprint_speed")
            player.save()

            if created:
                imported += 1
            else:
                updated += 1

    return (imported, updated, skipped)
