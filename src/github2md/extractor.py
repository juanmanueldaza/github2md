"""GitHub data extractor using gh CLI."""

import json
import subprocess
from typing import Any

from .protocols import DataExtractor


class GitHubExtractor(DataExtractor):
    """Extract GitHub data using gh CLI."""

    def __init__(self, token: str | None = None):
        self._token = token

    def _run_gh(self, *args: str) -> dict[str, Any]:
        """Run gh CLI command and return JSON response."""
        env = None
        if self._token:
            import os

            env = os.environ.copy()
            env["GH_TOKEN"] = self._token

        try:
            result = subprocess.run(
                ["gh", *args],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except subprocess.CalledProcessError as e:
            if "rate limit" in e.stderr.lower():
                raise RuntimeError("GitHub API rate limit exceeded") from None
            if "not found" in e.stderr.lower():
                raise RuntimeError("User or resource not found") from None
            raise RuntimeError("GitHub CLI command failed") from None
        except json.JSONDecodeError:
            return {}

    def extract(self, username: str) -> dict[str, Any]:
        """Extract all GitHub data for a user."""
        data: dict[str, Any] = {"username": username}
        data["profile"] = [self._get_profile(username)]
        data["repos"] = self._get_repos(username)
        data["contributions"] = self._get_contributions(username)
        return data

    def _get_profile(self, username: str) -> dict[str, Any]:
        """Get user profile."""
        return self._run_gh("api", f"/users/{username}")

    def _get_repos(self, username: str) -> list[dict[str, Any]]:
        """Get user repositories."""
        try:
            result = self._run_gh(
                "api", f"/users/{username}/repos", "-f", "per_page=100"
            )
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def _get_contributions(self, username: str) -> dict[str, Any]:
        """Get contribution data via GraphQL."""
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """
        try:
            result = self._run_gh(
                "api", "graphql", "-f", f"query={query}", "-f", f"login={username}"
            )
            user = result.get("data", {}).get("user", {})
            return user.get("contributionsCollection", {})
        except Exception:
            return {}


class DictExtractor(DataExtractor):
    """Extract data from a pre-populated dictionary (for testing)."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def extract(self, username: str) -> dict[str, Any]:
        return {**self._data, "username": username}
