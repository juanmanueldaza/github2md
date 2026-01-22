"""Shared constants for github2md."""

# Pagination limits
MAX_REPOS = 50
MAX_EXTERNAL_PRS = 20
MAX_EXTERNAL_ISSUES = 15
MAX_RECENT_PRS = 15
MAX_RECENT_ISSUES = 15
MAX_LANGUAGES = 20
MAX_FOLLOWERS = 30
MAX_FOLLOWING = 50
MAX_STARRED = 50
MAX_TOPICS = 30
MAX_GISTS = 20
MAX_ORGS = 20

# Text truncation
DEFAULT_TRUNCATE_LENGTH = 100

# URL security
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}

# PR state icons
PR_STATE_ICONS = {
    "MERGED": "\u2705",
    "OPEN": "\U0001F504",
    "CLOSED": "\u274C",
}

# Issue state icons
ISSUE_STATE_ICONS = {
    "OPEN": "\U0001F7E2",
    "CLOSED": "\U0001F7E3",
}
