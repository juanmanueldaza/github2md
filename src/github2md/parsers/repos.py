"""Repositories parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class ReposParser(BaseParser):
    """Parse repository data."""

    @property
    def section_key(self) -> str:
        return "repos"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        repos = raw_data.get("repos", [])
        parsed = []
        languages: dict[str, int] = {}
        total_stars = 0
        total_forks = 0

        for repo in repos:
            if repo.get("fork"):
                continue
            stars = repo.get("stargazers_count", 0) or repo.get("stars", 0)
            forks = repo.get("forks_count", 0) or repo.get("forks", 0)
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            total_stars += stars
            total_forks += forks
            parsed.append(
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "url": repo.get("html_url"),
                    "language": lang,
                    "stars": stars,
                    "forks": forks,
                    "topics": repo.get("topics", []),
                    "created_at": self._format_date(repo.get("created_at")),
                    "updated_at": self._format_date(repo.get("updated_at")),
                }
            )

        parsed.sort(key=lambda x: x.get("stars", 0), reverse=True)
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        return {
            "repos": parsed,
            "total": len(parsed),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "languages": dict(sorted_langs),
        }
