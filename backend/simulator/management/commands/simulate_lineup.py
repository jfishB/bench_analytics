"""
Management command to run baseball game simulations.
"""

from django.core.management.base import BaseCommand, CommandError

from simulator.application.simulation_service import SimulationService
from simulator.infrastructure.player_repository import PlayerRepository


class Command(BaseCommand):
    help = "Simulate baseball games with a given lineup of 9 players"

    def add_arguments(self, parser):
        parser.add_argument(
            "--player-ids",
            "-p",
            dest="player_ids",
            type=str,
            help="Comma-separated list of 9 player IDs (e.g., '1,2,3,4,5,6,7,8,9')",
        )
        parser.add_argument(
            "--player-names",
            "-n",
            dest="player_names",
            type=str,
            help="Comma-separated list of 9 player names (e.g., 'Player One,Player Two,...')",
        )
        parser.add_argument(
            "--team-id",
            "-t",
            dest="team_id",
            type=int,
            help="Use top 9 players from this team (by plate appearances)",
        )
        parser.add_argument(
            "--games",
            "-g",
            dest="num_games",
            type=int,
            default=1000,
            help="Number of games to simulate (default: 1000)",
        )

    def handle(self, *args, **options):
        player_ids = options.get("player_ids")
        player_names = options.get("player_names")
        team_id = options.get("team_id")
        num_games = options.get("num_games")

        # Validate that exactly one input method is provided
        inputs_provided = sum([
            bool(player_ids),
            bool(player_names),
            bool(team_id)
        ])
        
        if inputs_provided == 0:
            raise CommandError(
                "Must provide one of: --player-ids, --player-names, or --team-id"
            )
        
        if inputs_provided > 1:
            raise CommandError(
                "Provide only one of: --player-ids, --player-names, or --team-id"
            )

        # Initialize services
        repository = PlayerRepository()
        service = SimulationService()

        # Get player stats based on input method
        try:
            if player_ids:
                ids = [int(id.strip()) for id in player_ids.split(",")]
                if len(ids) != 9:
                    raise CommandError(f"Must provide exactly 9 player IDs, got {len(ids)}")
                
                self.stdout.write(f"Loading players by IDs: {ids}")
                batter_stats = repository.get_players_by_ids(ids)
                
            elif player_names:
                names = [name.strip() for name in player_names.split(",")]
                if len(names) != 9:
                    raise CommandError(f"Must provide exactly 9 player names, got {len(names)}")
                
                self.stdout.write(f"Loading players by names: {names}")
                batter_stats = repository.get_players_by_names(names)
                
            else:  # team_id
                self.stdout.write(f"Loading top 9 players from team {team_id}")
                batter_stats = repository.get_team_players(team_id, limit=9)
                
                if len(batter_stats) < 9:
                    raise CommandError(
                        f"Team {team_id} only has {len(batter_stats)} players, need 9"
                    )

        except ValueError as e:
            raise CommandError(str(e))

        # Display lineup
        self.stdout.write("\n" + self.style.SUCCESS("=== LINEUP ==="))
        for i, stats in enumerate(batter_stats, 1):
            self.stdout.write(
                f"{i}. {stats.name} "
                f"(PA: {stats.plate_appearances}, "
                f"H: {stats.hits}, "
                f"HR: {stats.home_runs}, "
                f"K: {stats.strikeouts}, "
                f"BB: {stats.walks})"
            )

        # Run simulation
        self.stdout.write(f"\n{self.style.WARNING(f'Running {num_games} simulations...')}")
        
        try:
            result = service.simulate_lineup(batter_stats, num_games=num_games)
        except Exception as e:
            raise CommandError(f"Simulation failed: {str(e)}")

        # Display results
        self.stdout.write("\n" + self.style.SUCCESS("=== RESULTS ==="))
        self.stdout.write(f"Games Simulated: {result.num_games}")
        self.stdout.write(f"Average Score:   {result.avg_score:.2f} runs/game")
        self.stdout.write(f"Median Score:    {result.median_score:.1f} runs/game")
        self.stdout.write(f"Std Deviation:   {result.std_dev:.2f}")
        
        # Show score distribution
        if result.all_scores:
            min_score = min(result.all_scores)
            max_score = max(result.all_scores)
            self.stdout.write(f"Score Range:     {min_score} - {max_score} runs")
            
            # Simple histogram
            self.stdout.write("\nScore Distribution:")
            score_counts = {}
            for score in result.all_scores:
                score_counts[score] = score_counts.get(score, 0) + 1
            
            for score in sorted(score_counts.keys())[:15]:  # Show first 15
                count = score_counts[score]
                pct = (count / len(result.all_scores)) * 100
                bar = "█" * int(pct / 2)  # Scale bar
                self.stdout.write(f"  {score:2d} runs: {bar} {pct:.1f}%")

        self.stdout.write("\n" + self.style.SUCCESS("✓ Simulation complete!"))
