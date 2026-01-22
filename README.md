# github2md

[![PyPI version](https://img.shields.io/pypi/v/github2md)](https://pypi.org/project/github2md/)
[![Python versions](https://img.shields.io/pypi/pyversions/github2md)](https://pypi.org/project/github2md/)
[![License](https://img.shields.io/pypi/l/github2md)](https://github.com/juanmanueldaza/github2md/blob/main/LICENSE)

Convert GitHub profile data to clean Markdown files - perfect for LLM analysis.

## Installation

```bash
pip install github2md
```

Requires GitHub CLI (`gh`) to be installed and authenticated.

## Usage

```bash
# Export your own profile
github2md

# Export a specific user
github2md torvalds

# Specify output directory
github2md -o my_export torvalds
```

## Output

Creates Markdown files for:
- **profile.md** - User profile information
- **repositories.md** - Repositories with stats
- **contributions.md** - Contribution statistics

## Requirements

- Python 3.13+
- GitHub CLI (`gh`) - Install from https://cli.github.com

## License

GPL-2.0
