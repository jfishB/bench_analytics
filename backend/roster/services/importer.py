import csv
from decimal import Decimal
from typing import Any, Dict, List, Optional

from roster.models import Player, Team


def _to_float(v):
    if v is None or v == "":
        return None
    try:
        return float(Decimal(v))
    except Exception:
        try:
            return float(str(v).replace("%", ""))
        except Exception:
            return None


def _to_int(v):
    if v is None or v == "":
        return None
    try:
        return int(Decimal(v))
    except Exception:
        try:
            return int(str(v).replace("%", ""))
        except Exception:
            return None


def import_from_csv(path: str, team_id: Optional[int]
                    = None, dry_run: bool = False) -> Dict[str, Any]:
    """Import players from a CSV file into the roster Player model.

    Returns a summary dict with counts and messages.
    """
    messages: List[str] = []
    try:
        f = open(path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        raise

    reader = csv.DictReader(f)
    rows = list(reader)
    if not rows:
        messages.append("No rows found in CSV.")
        f.close()
        return {"processed": 0, "created": 0, "updated": 0, "messages": messages}

    if team_id is not None:
        Team.objects.get_or_create(pk=team_id)

    processed = created = updated = 0

    for r in rows:
        name = r.get('"last_name, first_name"') or r.get(
            "last_name, first_name") or r.get("name")
        if name is None:
            first = r.get(" first_name") or r.get("first_name")
            last = r.get("last_name")
            if first and last:
                name = f"{last}, {first}"

        if not name:
            messages.append(f"Skipping row without name: {r}")
            continue

        savant_player_id = r.get("player_id") or r.get("savant_player_id")
        year = r.get("year")
        pa = r.get("pa")

        # Raw counting stats (for simulation)
        hit = r.get("hit")
        single = r.get("single")
        double = r.get("double")
        triple = r.get("triple")
        home_run = r.get("home_run")
        strikeout = r.get("strikeout")
        walk = r.get("walk")

        # Derived percentages
        k_percent = _to_float(r.get("k_percent"))
        bb_percent = _to_float(r.get("bb_percent"))
        slg_percent = _to_float(r.get("slg_percent"))
        on_base_percent = _to_float(r.get("on_base_percent"))
        isolated_power = _to_float(r.get("isolated_power"))
        b_total_bases = _to_int(r.get("b_total_bases"))
        r_total_caught_stealing = _to_int(r.get("r_total_caught_stealing"))
        r_total_stolen_base = _to_float(r.get("r_total_stolen_base"))
        b_game = _to_int(r.get("b_game"))
        b_gnd_into_dp = _to_int(r.get("b_gnd_into_dp"))
        b_hit_by_pitch = _to_int(r.get("b_hit_by_pitch"))
        b_intent_walk = _to_int(r.get("b_intent_walk"))
        b_sac_fly = _to_int(r.get("b_sac_fly"))
        b_sac_bunt = _to_int(r.get("b_sac_bunt"))

        team_id_csv = None
        if "team_id" in r:
            team_id_csv = r.get("team_id")
        elif '"team_id"' in r:
            team_id_csv = r.get('"team_id"')

        use_team_id = None
        if team_id_csv:
            try:
                use_team_id = int(team_id_csv)
            except Exception:
                use_team_id = None
        elif team_id is not None:
            use_team_id = team_id

        team_obj = None
        if use_team_id is not None:
            team_obj, _ = Team.objects.get_or_create(pk=use_team_id)

        defaults: Dict[str, Any] = {
            "savant_player_id": (
                int(savant_player_id)
                if savant_player_id and str(savant_player_id).isdigit()
                else None
            ),
            "year": int(year) if year and str(year).isdigit() else None,
            "pa": int(pa) if pa and str(pa).isdigit() else None,
            # Raw counting stats
            "hit": int(hit) if hit and str(hit).isdigit() else None,
            "single": int(single) if single and str(single).isdigit() else None,
            "double": int(double) if double and str(double).isdigit() else None,
            "triple": int(triple) if triple and str(triple).isdigit() else None,
            "home_run": int(home_run) if home_run and str(home_run).isdigit() else None,
            "strikeout": int(strikeout) if strikeout and str(strikeout).isdigit() else None,
            "walk": int(walk) if walk and str(walk).isdigit() else None,
            # Derived percentages
            "k_percent": k_percent,
            "bb_percent": bb_percent,
            "slg_percent": slg_percent,
            "on_base_percent": on_base_percent,
            "isolated_power": isolated_power,
            "b_total_bases": b_total_bases,
            "r_total_caught_stealing": r_total_caught_stealing,
            "r_total_stolen_base": r_total_stolen_base,
            "b_game": b_game,
            "b_gnd_into_dp": b_gnd_into_dp,
            "b_hit_by_pitch": b_hit_by_pitch,
            "b_intent_walk": b_intent_walk,
            "b_sac_fly": b_sac_fly,
            "b_sac_bunt": b_sac_bunt,
        }

        if dry_run:
            messages.append(
                f"Would import player: {name} team_id={use_team_id} fields={defaults}")
            processed += 1
            continue

        player, created_flag = Player.objects.update_or_create(
            name=name,
            defaults={**defaults, "team": team_obj},
        )
        processed += 1
        if created_flag:
            created += 1
        else:
            updated += 1

    f.close()
    messages.append(
        f"Processed {processed} rows: created={created} updated={updated}")
    return {"processed": processed, "created": created, "updated": updated, "messages": messages}
