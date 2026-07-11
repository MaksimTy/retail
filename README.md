# Retail Ontology Platform

A headless ontology platform for retail analytics, built as a reusable Python library with thin interface adapters.

## Architecture

This monorepo contains four packages:

- **retail-ontology** - Core library: concepts, metrics, relationships, query engine, data adapters, LLM providers
- **retail-cli** - Command-line interface (Typer + Rich)
- **retail-telegram** - Telegram bot wrapper (python-telegram-bot)
- **retail-api** - REST API wrapper (FastAPI + Uvicorn)

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - Detailed architecture documentation
- [API Reference](docs/API.md) - Core library API documentation
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment instructions (Docker, Kubernetes, Serverless)
- [Ontology Guide](docs/ONTOLOGY_GUIDE.md) - How to define concepts and metrics
- [Development Guide](docs/DEVELOPMENT.md) - Development workflow and best practices
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Detailed implementation roadmap
- [Questions & Clarifications](docs/QUESTIONS.md) - Open questions for the project

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
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # Architecture documentation
│   ├── API.md               # API reference
│   ├── DEPLOYMENT.md        # Deployment guide
│   ├── ONTOLOGY_GUIDE.md    # Ontology definition guide
│   ├── DEVELOPMENT.md       # Development guide
│   ├── IMPLEMENTATION_PLAN.md # Implementation roadmap
│   └── QUESTIONS.md         # Open questions
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

## Package Documentation

- [retail-ontology](packages/retail-ontology/README.md) - Core library
- [retail-cli](packages/retail-cli/README.md) - CLI wrapper
- [retail-telegram](packages/retail-telegram/README.md) - Telegram bot
- [retail-api](packages/retail-api/README.md) - REST API

## License

Apache-2.0
