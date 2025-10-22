from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from lineups.models import Player
import csv
from pathlib import Path


class Command(BaseCommand):
    help = "Load batter stats from CSV (data/batter_stats_2025.csv) into Player model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            default=str(Path.cwd() / "data" / "batter_stats_2025.csv"),
            help="Path to the CSV file to import",
        )

        parser.add_argument(
            "--year",
            dest="year",
            type=int,
            default=None,
            help="Optional year to set on imported rows (overrides CSV year)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Parse and report what would be imported without saving",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"CSV file not found: {file_path}")

        imported = 0
        updated = 0
        skipped = 0

        # Read CSV with BOM handling; csv.DictReader will normalize headers
        with file_path.open(newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)

        self.stdout.write(f"Found {len(rows)} rows in {file_path}")

        if options.get("dry_run"):
            # Show first row keys and sample values
            if rows:
                self.stdout.write("Sample row keys:")
                self.stdout.write(str(list(rows[0].keys())))
                self.stdout.write("\nFirst row data:")
                self.stdout.write(str(rows[0]))
            return

        with transaction.atomic():
            for r in rows:
                # The CSV uses quoted column: "last_name, first_name"
                # DictReader normalizes it to the exact string 'last_name, first_name' (without outer quotes)
                raw_name = r.get('last_name, first_name')
                if not raw_name:
                    skipped += 1
                    continue

                # Name is already in "Last, First" format in the CSV
                name = raw_name.strip()

                # Try to find existing player by exact name; fallback to creating new
                player, created = Player.objects.get_or_create(name=name)

                # Map CSV fields to Player model fields (safe parsing)
                def fflt(key):
                    v = r.get(key)
                    if v is None or v == "":
                        return None
                    # strip quotes and percent signs
                    try:
                        return float(str(v).replace('"','').replace('%','').strip())
                    except ValueError:
                        return None

                # integer fields
                try:
                    savant_id = int(r.get('player_id')) if r.get('player_id') else None
                except ValueError:
                    savant_id = None

                try:
                    pa = int(r.get('pa')) if r.get('pa') else None
                except ValueError:
                    pa = None

                # pick year override if provided
                year = options.get('year') if options.get('year') is not None else (int(r.get('year')) if r.get('year') else None)

                # set model fields
                player.savant_player_id = savant_id
                player.year = year
                player.pa = pa
                player.k_percent = fflt('k_percent')
                player.bb_percent = fflt('bb_percent')
                # woba/xwoba may be quoted like ".351"
                player.woba = fflt('woba')
                player.xwoba = fflt('xwoba')
                # barrel_batted_rate is the CSV column name for Barrel%
                player.barrel_batted_rate = fflt('barrel_batted_rate')

                player.save()

                if created:
                    imported += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"Imported={imported} Updated={updated} Skipped={skipped}"))