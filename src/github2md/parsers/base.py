"""Base parser with shared utilities."""

from typing import Any


class BaseParser:
    """Base class with utility methods for parsers."""

    def _safe_get(self, data: dict[str, Any], *keys: str, default: Any = None) -> Any:
        """Safely get nested dictionary values."""
        result = data
        for key in keys:
            if not isinstance(result, dict):
                return default
            result = result.get(key, default)
            if result is None:
                return default
        return result

    def _format_date(self, date_str: str | None) -> str | None:
        """Format ISO date string to readable format."""
        if not date_str:
            return None
        try:
            return date_str[:10]
        except Exception:
            return None
