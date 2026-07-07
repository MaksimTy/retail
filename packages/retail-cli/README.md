# retail-cli

Command-line interface for the Retail Ontology Platform.

## Features

- **ask** - Natural language queries via LLM
- **build** - Build DuckDB warehouse from source data
- **download** - Download UCI Online Retail dataset
- **config** - Manage configuration
- **models** - List available concepts and metrics

## Installation

```bash
# From monorepo root
uv sync --all-extras

# Or install directly
pip install retail-cli
```

## Usage

```bash
# Ask a question
retail ask "revenue by country"

# Build warehouse
retail build

# Download data
retail download

# Show configuration
retail config show

# List concepts
retail models concepts

# List metrics
retail models metrics
```

## Development

```bash
# Run CLI
uv run retail

# Run tests
uv run pytest packages/retail-cli/tests -v

# Type check
uv run mypy packages/retail-cli/src

# Build
cd packages/retail-cli && uv build
```

## Package Structure

```
retail-cli/
├── pyproject.toml
├── README.md
├── src/
│   └── retail_cli/
│       ├── __init__.py
│       ├── main.py              # Typer app entry point
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── ask.py           # ask command
│       │   ├── build.py         # build command
│       │   ├── download.py      # download command
│       │   ├── config.py        # config command
│       │   └── models.py        # models command
│       └── formatting.py        # Rich formatting utilities
└── tests/
    ├── test_ask.py
    ├── test_build.py
    ├── test_download.py
    └── test_config.py