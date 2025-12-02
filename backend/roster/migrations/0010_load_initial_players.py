"""
Data migration placeholder - data loading now handled via API endpoint.
The load_sample_players endpoint at /api/v1/roster/load-sample-players/
handles initial data loading for new deployments.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("roster", "0009_remove_player_position"),
    ]
    operations = []  # No-op - data loading handled via API
