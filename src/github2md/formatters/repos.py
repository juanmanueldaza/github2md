"""Repositories formatter."""

from typing import Any

from ..constants import MAX_REPOS
from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ReposFormatter(BaseFormatter):
    """Format repositories to Markdown."""

    @property
    def section_key(self) -> str:
        return "repos"

    @property
    def output_filename(self) -> str:
        return "repositories.md"

    def format(self, data: dict[str, Any]) -> str:
        repos = data.get("repos", [])
        total = data.get("total", 0)
        stars = data.get("total_stars", 0)
        forks = data.get("total_forks", 0)

        lines = [f"# Repositories ({total} total)\n"]
        lines.append(f"**Total Stars:** {stars} | **Total Forks:** {forks}\n")

        languages = data.get("languages", {})
        if languages:
            lines.append("## Languages\n")
            for lang, count in list(languages.items())[:10]:
                lines.append(f"- **{lang}:** {count} repos")
            lines.append("")

        if repos:
            lines.append("## Top Repositories\n")
            for repo in repos[:MAX_REPOS]:
                name = repo.get("name", "Unknown")
                url = repo.get("url", "")
                desc = self._truncate(repo.get("description"), 100)
                desc = desc or "No description"
                repo_stars = repo.get("stars", 0)
                lang = repo.get("language") or "Unknown"

                lines.append(f"### {self._make_link(name, url)}")
                lines.append(f"{desc}")
                lines.append(f"- **Language:** {lang} | **Stars:** {repo_stars}")
                lines.append("")

        return "\n".join(lines) + "\n"
