"""Command-line interface for github2md."""

import argparse
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

    username = args.username
    if not username:
        username = get_authenticated_user()
        if not username:
            print(
                "Error: No username provided and not authenticated.",
                file=sys.stderr,
            )
            print("Run 'gh auth login' first.", file=sys.stderr)
            sys.exit(1)
        print(f"Using authenticated user: {username}")

    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("Error: gh CLI not found.", file=sys.stderr)
        sys.exit(1)

    try:
        converter = create_converter(args.output)
        print(f"Fetching GitHub data for: {username}")
        files = converter.convert(username)
        print(f"\nCreated {len(files)} files in {args.output}/")
        for f in files:
            print(f"  - {f.name}")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
