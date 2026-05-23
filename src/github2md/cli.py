"""Command-line interface for github2md."""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from . import __version__
from .converter import create_converter


def get_authenticated_user():
    """Get the currently authenticated GitHub user via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", "/user", "--jq", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="github2md",
        description="Convert GitHub profile data to Markdown for LLM analysis",
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="GitHub username (defaults to authenticated user)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("github_export"),
        help="Output directory (default: github_export)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

    username = args.username
    if not username:
        username = get_authenticated_user()
        if not username:
            logging.error("No username provided and not authenticated.")
            logging.error("Run 'gh auth login' first.")
            sys.exit(1)
        logging.info("Using authenticated user: %s", username)

    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        logging.error("gh CLI not found.")
        sys.exit(1)

    try:
        converter = create_converter(args.output)
        logging.info("Fetching GitHub data for: %s", username)
        files = converter.convert(username)
        logging.info("Created %d files in %s/", len(files), args.output)
        for f in files:
            logging.info("  - %s", f.name)
    except (ValueError, RuntimeError) as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
