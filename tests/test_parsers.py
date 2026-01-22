"""Tests for parsers."""

import pytest
from github2md.parsers.profile import ProfileParser
from github2md.parsers.repos import ReposParser
from github2md.parsers.contributions import ContributionsParser


class TestProfileParser:
    def test_section_key(self):
        parser = ProfileParser()
        assert parser.section_key == "profile"

    def test_parse_profile(self):
        parser = ProfileParser()
        raw_data = {
            "profile": [{
                "login": "testuser",
                "name": "Test User",
                "bio": "A developer",
                "public_repos": 10,
            }]
        }
        result = parser.parse(raw_data)
        assert result["username"] == "testuser"
        assert result["name"] == "Test User"


class TestReposParser:
    def test_section_key(self):
        parser = ReposParser()
        assert parser.section_key == "repos"

    def test_parse_repos(self):
        parser = ReposParser()
        raw_data = {
            "repos": [
                {"name": "repo1", "stargazers_count": 10, "language": "Python"},
                {"name": "repo2", "stargazers_count": 5, "language": "Python"},
            ]
        }
        result = parser.parse(raw_data)
        assert result["total"] == 2
        assert result["total_stars"] == 15


class TestContributionsParser:
    def test_section_key(self):
        parser = ContributionsParser()
        assert parser.section_key == "contributions"

    def test_parse_contributions(self):
        parser = ContributionsParser()
        raw_data = {
            "contributions": {
                "totalCommitContributions": 100,
                "totalPullRequestContributions": 20,
            }
        }
        result = parser.parse(raw_data)
        assert result["total_commits"] == 100
        assert result["total_prs"] == 20
