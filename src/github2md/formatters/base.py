"""Base formatter with shared utilities."""

import urllib.parse

from ..constants import (
    ALLOWED_URL_SCHEMES,
    DEFAULT_TRUNCATE_LENGTH,
    ISSUE_STATE_ICONS,
    PR_STATE_ICONS,
)


class BaseFormatter:
    """Base class with utility methods for formatters."""

    def _escape_md(self, text: str | None) -> str:
        """Escape markdown special characters."""
        if not text:
            return ""
        return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")

    def _sanitize_url(self, url: str | None) -> str:
        """Sanitize URL for safe inclusion in Markdown."""
        if not url:
            return ""
        url = url.strip()
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme:
                return ""
            if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
                return ""
        except Exception:
            return ""
        return url.replace(")", "%29").replace("[", "%5B").replace("]", "%5D")

    def _make_link(self, text: str, url: str | None) -> str:
        """Create a markdown link with sanitized URL."""
        if not url:
            return text
        safe_url = self._sanitize_url(url)
        if not safe_url:
            return text
        return f"[{text}]({safe_url})"

    def _truncate(self, text: str | None, max_len: int = 100) -> str:
        """Truncate text to max length."""
        if max_len == 100:
            max_len = DEFAULT_TRUNCATE_LENGTH
        if not text:
            return ""
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def _get_pr_state_icon(self, state: str) -> str:
        """Get icon for PR state."""
        return PR_STATE_ICONS.get(state, "?")

    def _get_issue_state_icon(self, state: str) -> str:
        """Get icon for issue state."""
        return ISSUE_STATE_ICONS.get(state, "?")

    def _format_more(self, shown: int, total: int, item_type: str) -> str:
        """Format 'and X more' message."""
        remaining = total - shown
        if remaining <= 0:
            return ""
        return f"\n*...and {remaining} more {item_type}*\n"
