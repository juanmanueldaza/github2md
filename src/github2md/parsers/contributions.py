"""Contributions parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class ContributionsParser(BaseParser):
    """Parse contribution data."""

    @property
    def section_key(self) -> str:
        return "contributions"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        contrib = raw_data.get("contributions", {})
        calendar = contrib.get("contributionCalendar", {})
        return {
            "total_commits": contrib.get("totalCommitContributions", 0),
            "total_issues": contrib.get("totalIssueContributions", 0),
            "total_prs": contrib.get("totalPullRequestContributions", 0),
            "total_reviews": contrib.get("totalPullRequestReviewContributions", 0),
            "total_contributions": calendar.get("totalContributions", 0),
        }
