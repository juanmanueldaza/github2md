"""Profile formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ProfileFormatter(BaseFormatter):
    """Format profile to Markdown."""

    @property
    def section_key(self) -> str:
        return "profile"

    @property
    def output_filename(self) -> str:
        return "profile.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = [f"# GitHub Profile: {data.get('username', 'Unknown')}\n"]

        if data.get("name"):
            lines.append(f"**{data['name']}**\n")

        if data.get("bio"):
            lines.append(f"> {data['bio']}\n")

        lines.append("## Info\n")
        info = [
            ("Company", data.get("company")),
            ("Location", data.get("location")),
            ("Blog", data.get("blog")),
            ("Twitter", data.get("twitter")),
            ("Member since", data.get("created_at")),
        ]
        for label, value in info:
            if value:
                lines.append(f"- **{label}:** {value}")

        lines.append("\n## Stats\n")
        lines.append(f"- **Public Repos:** {data.get('public_repos', 0)}")
        lines.append(f"- **Followers:** {data.get('followers', 0)}")
        lines.append(f"- **Following:** {data.get('following', 0)}")

        if data.get("html_url"):
            lines.append(f"\n**Profile:** {data['html_url']}")

        return "\n".join(lines) + "\n"
