import os
from pathlib import Path

from django.apps import AppConfig


class RosterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "roster"

    def ready(self):
        """auto-loads csv data when django starts up.

        how to use:
        - set LOAD_CSV to your csv filename (e.g., batter_stats_2025.csv)
        - optionally set CSV_YEAR to override the year in the csv
        - if you don't set LOAD_CSV, nothing happens and server starts normally

        example:
            $env:LOAD_CSV='batter_stats_2025.csv'; $env:CSV_YEAR='2025'; python manage.py runserver

        or just start without it:
            python manage.py runserver
        """
        # Only run in the main process, not in reloader or migration processes
        if os.environ.get("RUN_MAIN") != "true":
            return

        # Check if CSV loading is requested via environment variable
        csv_filename = os.environ.get("LOAD_CSV", "").strip()

        if not csv_filename:
            return

        # Avoid running during migrations or if database isn't ready
        from django.db import connection
        from roster.models import Player

        try:
            # Check if database and table exist using Django's introspection API
            table_name = Player._meta.db_table
            if table_name not in connection.introspection.table_names():
                print("\n[Roster CSV] Database tables not found. Run migrations first: python manage.py migrate")
                return

        except Exception as e:
            # Database not available or not configured
            print(f"\n[Roster CSV] Skipping CSV load - database not ready: {e}")
            return

        from roster.services.load_csv import load_csv_file

        # Base path to the data directory
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        csv_path = data_dir / csv_filename

        try:
            if not csv_path.exists():
                print(f"\n[Roster CSV] Error: File not found - {csv_path}")
                return

            # Get year from environment or use CSV default
            year_str = os.environ.get("CSV_YEAR", "").strip()
            year = int(year_str) if year_str else None

            print(f"\n[Roster CSV] Loading {csv_filename}...")
            imported, updated, skipped = load_csv_file(csv_path, year=year)
            print(f"[Roster CSV] Success! Imported: {imported}, Updated: {updated}, Skipped: {skipped}\n")

        except ValueError as e:
            print(f"\n[Roster CSV] Invalid year value: {e}")
        except Exception as e:
            print(f"\n[Roster CSV] Error loading CSV: {e}")
