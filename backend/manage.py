#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def main():
    """Run administrative tasks."""

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # If `manage.py test` is invoked with no app labels, some environments
    # (CI or custom settings) may not discover tests as expected. To make
    # local usage more predictable, if the user runs `manage.py test` with
    # no additional arguments, default to testing the main backend apps.
    if len(sys.argv) >= 2 and sys.argv[1] == "test":
        # If there are no positional test labels after `test` (only flags),
        # default to running the main backend app tests. This also covers
        # invocations like `manage.py test -v2`.
        tail_args = sys.argv[2:]
        has_positional_label = any(not a.startswith("-") for a in tail_args)
        if not tail_args or not has_positional_label:
            # Add the apps we want to run tests for by default. Keep this
            # list in sync with INSTALLED_APPS if you add more backend apps.
            sys.argv.extend(["lineups", "roster", "project_tests"])

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
