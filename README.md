# Retail Ontology Platform

A headless ontology platform for retail analytics, built as a reusable Python library with thin interface adapters.

## Architecture

This monorepo contains four packages:

- **retail-ontology** - Core library: concepts, metrics, relationships, query engine, data adapters, LLM providers
- **retail-cli** - Command-line interface (Typer + Rich)
- **retail-telegram** - Telegram bot wrapper (python-telegram-bot)
- **retail-api** - REST API wrapper (FastAPI + Uvicorn)

## Quick Start

```bash
# Install dependencies
make install

# Download sample data (UCI Online Retail dataset)
make download

# Build DuckDB warehouse
make build-warehouse

# Ask a question via CLI
make run-cli ARGS="ask 'revenue by country'"

# Run API server
make run-api

# Run Telegram bot
make run-telegram
```

## Development

```bash
# Run all checks
make check

# Run tests
make test

# Format code
make format

# Type check
make typecheck

# Build packages
make build

# Publish to PyPI
make publish
```

## Project Structure

```
retail-ontology-platform/
├── packages/
│   ├── retail-ontology/     # Core library
│   ├── retail-cli/          # CLI wrapper
│   ├── retail-telegram/     # Telegram bot wrapper
│   └── retail-api/          # REST API wrapper
├── pyproject.toml           # Root workspace config
├── Makefile                 # Development commands
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .env.example             # Environment variables template
└── .python-version          # Python version (3.11)
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required:
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM providers
- `DUCKDB_PATH` - Path to DuckDB warehouse file

Optional:
- `POSTGRES_DSN` - PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `API_HOST`, `API_PORT` - API server configuration

## License

MIT
