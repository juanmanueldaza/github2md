"""Tests for CLI module."""

from unittest.mock import patch, MagicMock
from github2md.cli import get_authenticated_user, main


class TestGetAuthenticatedUser:
    def test_returns_username_on_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="testuser\n")
            result = get_authenticated_user()
            assert result == "testuser"

    def test_returns_none_on_failure(self):
        with patch("subprocess.run") as mock_run:
            from subprocess import CalledProcessError
            mock_run.side_effect = CalledProcessError(1, "gh")
            result = get_authenticated_user()
            assert result is None
