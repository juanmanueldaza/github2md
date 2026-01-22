"""Contributions formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ContributionsFormatter(BaseFormatter):
    """Format contributions to Markdown."""

    @property
    def section_key(self) -> str:
        return "contributions"

    @property
    def output_filename(self) -> str:
        return "contributions.md"

    def format(self, data: dict[str, Any]) -> str:
        total = data.get("total_contributions", 0)
        lines = ["# Contributions\n"]
        lines.append(f"**Total Contributions (last year):** {total}\n")
        lines.append("## Breakdown\n")
        lines.append(f"- **Commits:** {data.get('total_commits', 0)}")
        lines.append(f"- **Pull Requests:** {data.get('total_prs', 0)}")
        lines.append(f"- **Issues:** {data.get('total_issues', 0)}")
        lines.append(f"- **Code Reviews:** {data.get('total_reviews', 0)}")
        return "\n".join(lines) + "\n"
