# This migration was replaced to match the current project layout.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lineups", "0001_initial"),
        ("roster", "0001_initial"),
    ]

    operations = []
