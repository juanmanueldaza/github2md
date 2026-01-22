"""github2md - Convert GitHub profile data to Markdown."""

try:
    from importlib.metadata import version
    __version__ = version("github2md")
except Exception:
    __version__ = "0.1.0"
