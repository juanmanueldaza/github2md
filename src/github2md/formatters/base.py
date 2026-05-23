"""Base formatter with shared utilities."""

import urllib.parse

from ..constants import ALLOWED_URL_SCHEMES, DEFAULT_TRUNCATE_LENGTH


class BaseFormatter:
    """Base class with utility methods for formatters."""

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
