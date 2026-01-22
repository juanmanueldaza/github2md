"""Main orchestrator for GitHub to Markdown conversion."""

import sys
from pathlib import Path
from typing import Any

from . import formatters, parsers  # noqa: F401
from .extractor import GitHubExtractor
from .protocols import DataExtractor, OutputWriter
from .registry import get_formatter_registry, get_parser_registry
from .writer import MarkdownFileWriter


class GitHubToMarkdownConverter:
    """Convert GitHub profile data to Markdown files."""

    def __init__(self, extractor: DataExtractor, writer: OutputWriter) -> None:
        self._extractor = extractor
        self._writer = writer
        self._parser_registry = get_parser_registry()
        self._formatter_registry = get_formatter_registry()

    def convert(self, username: str) -> list[Path]:
        """Convert GitHub data for a user to Markdown files."""
        raw_data = self._extractor.extract(username)
        parsed = self._parse_all(raw_data)
        return self._format_and_write_all(parsed)

    def _parse_all(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Parse all sections using registered parsers."""
        parsed: dict[str, Any] = {}
        for parser in self._parser_registry.get_all():
            try:
                parsed[parser.section_key] = parser.parse(raw_data)
            except Exception as e:
                key = parser.section_key
                print(f"Warning: Parser '{key}' failed: {e}", file=sys.stderr)
                parsed[parser.section_key] = None
        return parsed

    def _format_and_write_all(self, parsed: dict[str, Any]) -> list[Path]:
        """Format and write all sections using registered formatters."""
        created_files: list[Path] = []
        for formatter in self._formatter_registry.get_all():
            section_data = parsed.get(formatter.section_key)
            if section_data is None:
                continue
            try:
                markdown = formatter.format(section_data)
                if markdown and markdown.strip():
                    path = self._writer.write(formatter.output_filename, markdown)
                    created_files.append(path)
            except Exception as e:
                key = formatter.section_key
                print(f"Warning: Formatter '{key}' failed: {e}", file=sys.stderr)
        return created_files


def create_converter(output_dir: Path) -> GitHubToMarkdownConverter:
    """Factory function to create a converter with default dependencies."""
    extractor = GitHubExtractor()
    writer = MarkdownFileWriter(output_dir)
    return GitHubToMarkdownConverter(extractor, writer)
