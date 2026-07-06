# Project Structure Specification

## Complete Directory Tree

```
retail/
├── pyproject.toml              # uv project config (to be updated)
├── uv.lock
├── README.md
├── ARCHITECTURE.md             # Architecture documentation
├── .env.example                # Environment template
├── .gitignore
├── Makefile                    # Common commands
│
├── src/
│   └── retail/
│       ├── __init__.py
│       ├── __main__.py         # CLI entry point
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py     # Pydantic settings
│       │   └── logging.py
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   ├── source/
│       │   │   ├── __init__.py
│       │   │   ├── uci_downloader.py
│       │   │   └── validators.py
│       │   ├── staging/
│       │   │   ├── __init__.py
│       │   │   └── cleaner.py
│       │   ├── warehouse/
│       │   │   ├── __init__.py
│       │   │   ├── models.py       # SQLAlchemy models
│       │   │   ├── schema.py       # DDL
│       │   │   └── loader.py       # ETL loader
│       │   └── access/
│       │       ├── __init__.py
│       │       ├── repository.py   # Data access patterns
│       │       └── queries.py      # Pre-built queries
│       │
│       ├── ontology/
│       │   ├── __init__.py
│       │   ├── concepts/
│       │   │   ├── __init__.py
│       │   │   ├── registry.py
│       │   │   └── definitions.yaml
│       │   ├── metrics/
│       │   │   ├── __init__.py
│       │   │   ├── registry.py
│       │   │   └── definitions.yaml
│       │   ├── relationships/
│       │   │   ├── __init__.py
│       │   │   └── graph.py
│       │   └── query_builder/
│       │       ├── __init__.py
│       │       ├── translator.py   # NL → Query
│       │       ├── prompts.py      # Few-shot prompts
│       │       └── validator.py    # Query validation
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── core.py             # Agent orchestration
│       │   ├── llm/
│       │   │   ├── __init__.py
│       │   │   ├── base.py         # Abstract provider
│       │   │   ├── openai.py
│       │   │   ├── anthropic.py
│       │   │   ├── ollama.py
│       │   │   ├── llamacpp.py
│       │   │   └── factory.py      # Provider factory
│       │   ├── conversation.py     # Context management
│       │   └── tools.py            # Function calling tools
│       │
│       ├── interfaces/
│       │   ├── __init__.py
│       │   ├── cli/
│       │   │   ├── __init__.py
│       │   │   ├── app.py          # Typer/Click app
│       │   │   ├── commands.py
│       │   │   └── formatters.py
│       │   ├── telegram/
│       │   │   ├── __init__.py
│       │   │   ├── bot.py
│       │   │   ├── handlers.py
│       │   │   └── middleware.py
│       │   └── api/                # Future
│       │       ├── __init__.py
│       │       └── routes.py
│       │
│       └── deployment/
│           ├── __init__.py
│           ├── docker/
│           │   ├── Dockerfile
│           │   └── docker-compose.yml
│           └── scripts/
│               ├── setup.sh
│               ├── download_data.py
│               └── build_warehouse.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_data/
│   │   ├── test_ontology/
│   │   ├── test_agent/
│       │   └── test_interfaces/
│   ├── integration/
│   │   ├── test_e2e_cli.py
│   │   └── test_e2e_telegram.py
│   └── fixtures/
│       └── sample_data.csv
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   └── ontology_guide.md
│
└── scripts/
    ├── download_data.py
    ├── build_warehouse.py
    └── run_tests.py
```

## Module Responsibilities

### `retail.config`
- **settings.py**: Pydantic BaseSettings for all configuration (LLM, DB, Telegram, etc.)
- **logging.py**: Structured logging setup with loguru

### `retail.data.source`
- **uci_downloader.py**: Download Online Retail dataset (ID 352) via ucimlrepo
- **validators.py**: Validate raw data schema, check for anomalies

### `retail.data.staging`
- **cleaner.py**: Clean raw data (handle nulls, duplicates, type conversions)

### `retail.data.warehouse`
- **models.py**: SQLAlchemy ORM models for dim_customer, dim_product, fact_sales
- **schema.py**: DDL statements for DuckDB
- **loader.py**: ETL pipeline: staging → warehouse (Kimball dimensional model)

### `retail.data.access`
- **repository.py**: Repository pattern for typed data access
- **queries.py**: Pre-built analytical queries (revenue by country, top products, etc.)

### `retail.ontology.concepts`
- **registry.py**: Concept registry with metadata
- **definitions.yaml**: Business concept definitions (Customer, Product, Order, etc.)

### `retail.ontology.metrics`
- **registry.py**: Metric registry with computation logic
- **definitions.yaml**: Metric definitions (Total Revenue, AOV, Repeat Rate, etc.)

### `retail.ontology.relationships`
- **graph.py**: NetworkX graph of entity relationships, join paths

### `retail.ontology.query_builder`
- **translator.py**: NL → Structured Query (SQL/IR) using LLM + ontology
- **prompts.py**: Few-shot prompts for query generation
- **validator.py**: Validate generated queries against ontology

### `retail.agent.llm`
- **base.py**: Abstract LLMProvider interface
- **openai.py**: OpenAI API implementation
- **anthropic.py**: Anthropic API implementation
- **ollama.py**: Ollama local implementation
- **llamacpp.py**: llama.cpp local implementation
- **factory.py**: Provider factory from config

### `retail.agent`
- **core.py**: Main agent orchestration (question → query → answer)
- **conversation.py**: Conversation history, context management
- **tools.py**: Function calling tools for agent

### `retail.interfaces.cli`
- **app.py**: Typer application with commands
- **commands.py**: Command implementations
- **formatters.py**: Rich output formatting (tables, panels, etc.)

### `retail.interfaces.telegram`
- **bot.py**: Bot initialization and startup
- **handlers.py**: Command/message handlers
- **middleware.py**: Auth, rate limiting, logging middleware

### `retail.deployment.scripts`
- **download_data.py**: Standalone script to download UCI data
- **build_warehouse.py**: Standalone script to build DuckDB warehouse
- **setup.sh**: Environment setup script

## Configuration Files

### `.env.example`
```env
# LLM Configuration
LLM_PROVIDER=ollama          # openai, anthropic, ollama, llamacpp, vllm
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=                 # for cloud providers
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096

# Data
DUCKDB_PATH=./data/warehouse.duckdb
UCI_DATASET_ID=352

# Telegram (Phase 2)
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USERS=      # comma-separated user IDs

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json              # json or console
```

### `Makefile`
```makefile
.PHONY: help install dev-install test lint typecheck clean download build run-cli run-bot

help:
	@echo "Available commands:"
	@echo "  install       - Install production dependencies"
	@echo "  dev-install   - Install with dev dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run ruff linter"
	@echo "  typecheck     - Run mypy type checker"
	@echo "  clean         - Clean build artifacts"
	@echo "  download      - Download UCI dataset"
	@echo "  build         - Build data warehouse"
	@echo "  run-cli       - Run CLI interface"
	@echo "  run-bot       - Run Telegram bot"

install:
	uv sync

dev-install:
	uv sync --all-extras

test:
	uv run pytest -v

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src

clean:
	rm -rf .mypy_cache .pytest_cache __pycache__ src/**/__pycache__ tests/**/__pycache__
	rm -rf dist build *.egg-info

download:
	uv run retail-download

build:
	uv run retail-build

run-cli:
	uv run retail

run-bot:
	uv run retail-telegram
```

## Implementation Priority Order

1. **Config & Settings** (`retail.config`)
2. **Data Source** (`retail.data.source.uci_downloader`)
3. **Data Warehouse Models** (`retail.data.warehouse.models`)
4. **Data Warehouse Loader** (`retail.data.warehouse.loader`)
5. **Ontology Definitions** (`retail.ontology.concepts.definitions.yaml`, `retail.ontology.metrics.definitions.yaml`)
6. **Ontology Registry** (`retail.ontology.concepts.registry`, `retail.ontology.metrics.registry`)
7. **LLM Provider Abstraction** (`retail.agent.llm.base`, `retail.agent.llm.factory`, `retail.agent.llm.ollama`)
8. **Query Builder** (`retail.ontology.query_builder.translator`, `retail.ontology.query_builder.prompts`)
9. **Agent Core** (`retail.agent.core`)
10. **CLI Interface** (`retail.interfaces.cli.app`, `retail.interfaces.cli.commands`)
11. **Deployment Scripts** (`retail.deployment.scripts.download_data`, `retail.deployment.scripts.build_warehouse`)
12. **Telegram Bot** (`retail.interfaces.telegram.bot`, `retail.interfaces.telegram.handlers`)