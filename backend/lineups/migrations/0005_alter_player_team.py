# This migration was superseded by the roster initial migration which
# creates the Player.team field as nullable. Keep a no-op migration to
# preserve ordering if needed.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lineups", "0001_initial"),
    ]

    operations = []
