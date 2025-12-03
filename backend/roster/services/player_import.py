import csv
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.db import transaction

from roster.models import Player, Team


class PlayerImportService:
    """Service for importing players from CSV files."""

    @staticmethod  # pragma: no cover
    def import_from_csv(
        path: str | Path, team_id: Optional[int] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Import players from a CSV file into the roster Player model.

        Args:
            path: Path to the CSV file
            team_id: Optional team ID to assign to all players
            dry_run: If True, simulate import without saving

        Returns:
            Dict containing import summary (processed, created, updated, messages)
        """
        messages: List[str] = []
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            with file_path.open(newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")

        if not rows:
            return {
                "processed": 0,
                "created": 0,
                "updated": 0,
                "messages": ["No rows found in CSV."],
            }

        # Pre-fetch or create team if provided globally
        global_team = None
        if team_id is not None:
            global_team, _ = Team.objects.get_or_create(pk=team_id)

        processed = 0
        created_count = 0
        updated_count = 0

        # Use transaction for data integrity (unless dry_run)
        try:
            with transaction.atomic():
                for r in rows:
                    # 1. Extract Name
                    name = PlayerImportService._extract_name(r)
                    if not name:
                        messages.append(f"Skipping row without name: {r}")
                        continue

                    # 2. Determine Team
                    team_obj = PlayerImportService._determine_team(r, global_team)

                    # 3. Prepare Data
                    defaults = PlayerImportService._prepare_player_data(r)

                    if dry_run:
                        messages.append(
                            f"Would import player: {name} team={team_obj.id if team_obj else 'None'} fields={defaults}"
                        )
                        processed += 1
                        continue

                    # 4. Update or Create
                    player, created = Player.objects.update_or_create(
                        name=name,
                        defaults={**defaults, "team": team_obj},
                    )

                    processed += 1
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                if dry_run:
                    # Rollback is implicit since we didn't write, but good to be explicit mentally
                    pass

        except Exception as e:
            if not dry_run:
                messages.append(f"Import failed: {e}")
                raise e

        messages.append(
            f"Processed {processed} rows: created={created_count} updated={updated_count}"
        )
        return {
            "processed": processed,
            "created": created_count,
            "updated": updated_count,
            "messages": messages,
        }

    @staticmethod # pragma: no cover
    def _extract_name(row: Dict[str, Any]) -> Optional[str]:
        """Extract and normalize player name from row."""
        name = (
            row.get('"last_name, first_name"')
            or row.get("last_name, first_name")
            or row.get("name")
        )
        
        # If name is None or empty string, try to construct from parts
        if not name:
            first = row.get(" first_name") or row.get("first_name")
            last = row.get("last_name")
            if first and last:
                name = f"{last}, {first}"
        
        return name.strip() if name else None

    @staticmethod # pragma: no cover
    def _determine_team(row: Dict[str, Any], global_team: Optional[Team]) -> Optional[Team]: 
        """Determine team for the player."""
        team_id_csv = None
        if "team_id" in row:
            team_id_csv = row.get("team_id")
        elif '"team_id"' in row:
            team_id_csv = row.get('"team_id"')

        if team_id_csv:
            try:
                tid = int(team_id_csv)
                team, _ = Team.objects.get_or_create(pk=tid)
                return team
            except Exception:
                pass
        
        return global_team

    @staticmethod # pragma: no cover
    def _prepare_player_data(r: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and convert CSV row data into model fields."""
        
        def _to_float(v):
            if v is None or v == "":
                return None
            try:
                return float(Decimal(v))
            except Exception:
                try:
                    return float(str(v).replace("%", "").replace('"', ""))
                except Exception:
                    return None

        def _to_int(v):
            if v is None or v == "":
                return None
            try:
                return int(Decimal(v))
            except Exception:
                try:
                    return int(float(str(v).replace("%", "").replace('"', "")))
                except Exception:
                    return None

        # Helper to get value from row with fallback
        def get_val(key):
            return r.get(key)

        return {
            "savant_player_id": _to_int(get_val("player_id") or get_val("savant_player_id")),
            "year": _to_int(get_val("year")),
            "pa": _to_int(get_val("pa")),
            # Raw counting stats
            "hit": _to_int(get_val("hit")),
            "single": _to_int(get_val("single")),
            "double": _to_int(get_val("double")),
            "triple": _to_int(get_val("triple")),
            "home_run": _to_int(get_val("home_run")),
            "strikeout": _to_int(get_val("strikeout")),
            "walk": _to_int(get_val("walk")),
            # Derived percentages
            "k_percent": _to_float(get_val("k_percent")),
            "bb_percent": _to_float(get_val("bb_percent")),
            "slg_percent": _to_float(get_val("slg_percent")),
            "on_base_percent": _to_float(get_val("on_base_percent")),
            "isolated_power": _to_float(get_val("isolated_power")),
            "b_total_bases": _to_int(get_val("b_total_bases")),
            "r_total_caught_stealing": _to_int(get_val("r_total_caught_stealing")),
            "r_total_stolen_base": _to_float(get_val("r_total_stolen_base")),
            "b_game": _to_int(get_val("b_game")),
            "b_gnd_into_dp": _to_int(get_val("b_gnd_into_dp")),
            "b_hit_by_pitch": _to_int(get_val("b_hit_by_pitch")),
            "b_intent_walk": _to_int(get_val("b_intent_walk")),
            "b_sac_fly": _to_int(get_val("b_sac_fly")),
            "b_sac_bunt": _to_int(get_val("b_sac_bunt")),
        }
