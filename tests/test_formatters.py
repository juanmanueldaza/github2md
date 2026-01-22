"""Tests for formatters."""

import pytest
from github2md.formatters.profile import ProfileFormatter
from github2md.formatters.repos import ReposFormatter
from github2md.formatters.contributions import ContributionsFormatter


class TestProfileFormatter:
    def test_section_key(self):
        formatter = ProfileFormatter()
        assert formatter.section_key == "profile"

    def test_output_filename(self):
        formatter = ProfileFormatter()
        assert formatter.output_filename == "profile.md"

    def test_format_profile(self):
        formatter = ProfileFormatter()
        data = {
            "username": "testuser",
            "name": "Test User",
            "bio": "A developer",
        }
        result = formatter.format(data)
        assert "# GitHub Profile: testuser" in result
        assert "Test User" in result


class TestReposFormatter:
    def test_section_key(self):
        formatter = ReposFormatter()
        assert formatter.section_key == "repos"

    def test_format_repos(self):
        formatter = ReposFormatter()
        data = {
            "repos": [{"name": "repo1", "url": "https://github.com/user/repo1"}],
            "total": 1,
            "total_stars": 10,
            "total_forks": 5,
            "languages": {"Python": 1},
        }
        result = formatter.format(data)
        assert "# Repositories" in result
        assert "repo1" in result


class TestContributionsFormatter:
    def test_section_key(self):
        formatter = ContributionsFormatter()
        assert formatter.section_key == "contributions"

    def test_format_contributions(self):
        formatter = ContributionsFormatter()
        data = {
            "total_contributions": 500,
            "total_commits": 400,
            "total_prs": 50,
        }
        result = formatter.format(data)
        assert "# Contributions" in result
        assert "500" in result
