from django.core.management.base import BaseCommand
from lineups.models import Player
from lineups.utils.sort_sample import sort_players_by_wos, calculate_wos


class Command(BaseCommand):
    help = "Sort players by Weighted Offensive Score (WOS) and display top performers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--top",
            dest="top",
            type=int,
            default=10,
            help="Number of top players to display (default: 10)",
        )

        parser.add_argument(
            "--ascending",
            action="store_true",
            dest="ascending",
            help="Sort ascending (lowest WOS first) instead of descending",
        )

    def handle(self, *args, **options):
        top_n = options.get("top", 10)
        ascending = options.get("ascending", False)

        # Fetch all players from database
        players = Player.objects.all().values(
            "name", "savant_player_id", "xwoba", "bb_percent", "barrel_batted_rate", "k_percent"
        )
        players_list = list(players)

        if not players_list:
            self.stdout.write(self.style.WARNING("No players found in database."))
            return

        # Sort by WOS
        sorted_players = sort_players_by_wos(players_list, ascending=ascending)

        # Display results
        sort_order = "ascending" if ascending else "descending"
        self.stdout.write(
            self.style.SUCCESS(f"\n🏟️  Top {top_n} Players by WOS ({sort_order})\n")
        )
        self.stdout.write(f"{'Rank':<5} {'Player Name':<20} {'xwOBA':<8} {'BB%':<6} {'Barrel%':<8} {'K%':<6} {'WOS Score':<10}")
        self.stdout.write("-" * 80)

        for idx, player in enumerate(sorted_players[:top_n], 1):
            wos = calculate_wos(player)
            self.stdout.write(
                f"{idx:<5} {player['name']:<20} {player.get('xwoba', 0) or 0:<8.3f} "
                f"{player.get('bb_percent', 0) or 0:<6.1f} {player.get('barrel_batted_rate', 0) or 0:<8.1f} "
                f"{player.get('k_percent', 0) or 0:<6.1f} {wos:<10.2f}"
            )

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(f"Total players ranked: {len(sorted_players)}")
