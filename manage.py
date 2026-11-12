#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
    # Load the local development secret key.
    env_file = Path(__file__).resolve().parent / ".env"

    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("DJANGO_SECRET_KEY="):
                os.environ.setdefault(
                    "DJANGO_SECRET_KEY",
                    line.split("=", 1)[1],
                )
                break

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
