# AGENTS.md

Coding standards and conventions for github2md.

## Tech Stack

- **Language:** Python 3.13+
- **Build system:** Hatchling via `pyproject.toml`
- **Linting:** Ruff (line length: 88)
- **Type checking:** Pyright (strict)
- **Testing:** pytest
- **Dependencies:** None at runtime (only `dev` group)

## Project Structure

```
github2md/
├── src/github2md/         # Main package
│   ├── cli.py             # CLI entry point (argparse)
│   ├── converter.py       # Orchestrator (convert → parse → format → write)
│   ├── extractor.py       # Data extraction via gh CLI
│   ├── protocols.py       # Protocol classes (interfaces)
│   ├── registry.py        # Decorator-based plugin registration
│   ├── writer.py          # File output with security validation
│   ├── constants.py       # Shared constants
│   ├── formatters/        # Markdown formatters (one per section)
│   └── parsers/           # Data parsers (one per section)
├── tests/                 # pytest test suite
├── main.py                # Placeholder entry point
└── docs/                  # Static documentation site
```

## Coding Standards

### Formatting & Linting

- Line length: **88 characters**
- Run before committing: `ruff check . && ruff format --check . && pyright && pytest`

### Type Annotations

- All functions must have type annotations for parameters and return types.
- Use `from __future__ import annotations` style where applicable.
- Use `Any` from `typing` when types are dynamic.
- Mark protocols with `@runtime_checkable`.

### Naming Conventions

- **Modules:** `snake_case.py` (e.g., `cli.py`, `extractor.py`)
- **Classes:** `PascalCase` (e.g., `GitHubExtractor`, `ProfileParser`)
- **Functions/methods:** `snake_case` (e.g., `get_authenticated_user`, `_escape_md`)
- **Private members:** Prefix with `_` (e.g., `self._extractor`, `self._run_gh`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_REPOS`, `ALLOWED_URL_SCHEMES`)
- **Protocols:** Descriptive noun (e.g., `DataExtractor`, `OutputWriter`)
- **Type params:** Single uppercase letter (e.g., `T` in `register_parser[T]`)

### Docstrings

- Use triple-quoted `"""docstrings"""` for modules, classes, and public methods.
- First line should be a summary sentence ending with a period.
- Follow with `Args:`, `Returns:`, and `Raises:` sections using Google style.
- Private methods may omit docstrings if their purpose is obvious.

### Imports

Order:
1. Standard library (e.g., `import argparse`, `from pathlib import Path`)
2. Third-party (none currently)
3. Local (e.g., `from .protocols import DataExtractor`, `from ..registry import register_parser`)

### Error Handling

- Use specific exception types (`ValueError`, `RuntimeError`) — avoid bare `except:`.
- Print warnings to `sys.stderr` in orchestrator code.
- Wrap external command calls and JSON parsing in try/except.
- Validate filenames for path traversal (see `writer.py`).

## Architecture Conventions

### SOLID Principles

- **Single Responsibility:** Each parser/formatter handles exactly one section.
- **Open/Closed:** New parsers/formatters register via `@register_parser` / `@register_formatter` decorators — no modification of existing code.
- **Liskov Substitution:** All parsers implement `SectionParser` protocol, all formatters implement `SectionFormatter`.
- **Interface Segregation:** Separate protocols for `DataExtractor`, `SectionParser`, `SectionFormatter`, `OutputWriter`.
- **Dependency Inversion:** `GitHubToMarkdownConverter` depends on protocol abstractions, not concrete implementations.

### Registration Pattern

```python
# parsers/profile.py
@register_parser
class ProfileParser(BaseParser):
    section_key = "profile"

    def parse(self, raw_data: dict) -> dict:
        ...
```

- Add new sections by creating a parser + formatter pair in their respective directories.
- Parsers auto-register on import (triggered by `parsers/__init__.py` imports).

### Protocol Definitions

Protocols live in `protocols.py`. Implementations must satisfy the protocol structurally (no explicit inheritance required, but recommended for clarity).

### Error Resilience

- Parsers and formatters are wrapped in try/except in the converter.
- A failing parser produces `None` for that section; the corresponding formatter is then skipped.
- Extractors should handle API errors gracefully and return empty data structures.

## Testing Conventions

- Tests live in `tests/` and mirror the `src/github2md/` structure.
- Use plain `assert` statements (no `self.assertEqual`).
- Prefer `unittest.mock` (patch, MagicMock) for mocking external calls.
- Test files are named `test_<module>.py`.
- Each class tests one module; each method tests one behavior.
