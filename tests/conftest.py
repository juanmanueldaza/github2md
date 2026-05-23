"""Test helpers and fixtures."""

from pathlib import Path
from typing import Any

from github2md.protocols import DataExtractor, OutputWriter


class DictExtractor(DataExtractor):
    """Extract data from a pre-populated dictionary (for testing)."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def extract(self, username: str) -> dict[str, Any]:
        return {**self._data, "username": username}


class InMemoryWriter(OutputWriter):
    """In-memory writer for testing."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def write(self, filename: str, content: str) -> Path:
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        self.files[filename] = content
        return Path(filename)
