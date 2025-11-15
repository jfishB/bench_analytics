from django.core.management.base import BaseCommand, CommandError

from roster.services.importer import import_from_csv


class Command(BaseCommand):
    help = "Import test roster CSV into Player/Team models."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", "-f", dest="file", required=True, help="Path to CSV file to import"
        )
        parser.add_argument(
            "--team-id",
            "-t",
            dest="team_id",
            type=int,
            default=None,
            help="Team id to assign to all players unless CSV includes a team_id column",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Parse and show what would be imported without saving to DB",
        )

    def handle(self, *args, **options):
        path = options.get("file")
        team_id_arg = options.get("team_id")
        dry_run = options.get("dry_run")

        try:
            result = import_from_csv(path, team_id=team_id_arg, dry_run=dry_run)
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        for m in result.get("messages", []):
            self.stdout.write(m)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import summary: processed={result.get('processed')} created={result.get('created')} updated={result.get('updated')}"
            )
        )
