"""Profile parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class ProfileParser(BaseParser):
    """Parse user profile data."""

    @property
    def section_key(self) -> str:
        return "profile"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        profile_list = raw_data.get("profile", [])
        profile = profile_list[0] if profile_list else {}
        return {
            "username": profile.get("login") or raw_data.get("username"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "blog": profile.get("blog"),
            "email": profile.get("email"),
            "twitter": profile.get("twitter_username"),
            "public_repos": profile.get("public_repos", 0),
            "public_gists": profile.get("public_gists", 0),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "created_at": self._format_date(profile.get("created_at")),
            "html_url": profile.get("html_url"),
        }
