# retail-ontology

Core library for the Retail Ontology Platform - concepts, metrics, relationships, query engine, and data adapters.

## Features

- **Concepts Registry** - Define business entities (Customer, Product, Sale) with attributes, primary keys, foreign keys
- **Metrics Registry** - Define business metrics (Revenue, AOV, Repeat Rate) with expressions, grain, formatting
- **Relationships Graph** - NetworkX-based join path computation and validation
- **Data Adapters** - DuckDB (primary), PostgreSQL, Snowflake adapters with connection pooling
- **LLM Providers** - OpenRouter (first-class), OpenAI, Anthropic, Ollama, LlamaCpp
- **Query Engine** - Logical Query Plan (LQP) for NL→SQL translation
- **Data Scripts** - UCI dataset download and Kimball dimensional model build

## Installation

```bash
# From monorepo root
uv sync --all-extras

# Or install directly
pip install retail-ontology
pip install retail-ontology[postgres]  # with PostgreSQL adapter
pip install retail-ontology[snowflake]  # with Snowflake adapter
pip install retail-ontology[all]  # all adapters
```

## Quick Start

```python
from retail_ontology import RetailOntology

# Initialize
ontology = RetailOntology(config_path="config.yaml")

# Ask a question
result = ontology.ask("revenue by country")
print(result)

# Build warehouse
ontology.build_warehouse()

# Download data
ontology.download_data()
```

## CLI Commands

```bash
# Download UCI dataset
retail download

# Build DuckDB warehouse
retail build

# Ask a question
retail ask "revenue by country"

# List concepts
retail concepts

# List metrics
retail metrics

# Show config
retail config
```

## Configuration

Create a `config.yaml` or use environment variables:

```yaml
llm:
  provider: openrouter
  model: anthropic/claude-3.5-sonnet
  api_key: ${OPENROUTER_API_KEY}

database:
  adapter: duckdb
  duckdb_path: ./data/warehouse.duckdb

concepts:
  - name: Customer
    table: dim_customer
    primary_key: customer_key
    attributes:
      - name: customer_key
        type: integer
      - name: country
        type: string
      - name: customer_id
        type: string

metrics:
  - name: Revenue
    expression: sum(fact_sale.amount)
    grain: day
    format: currency
```

## Package Structure

```
retail-ontology/
├── pyproject.toml
├── README.md
├── src/
│   └── retail_ontology/
│       ├── __init__.py
│       ├── config.py              # Pydantic Settings
│       ├── concepts/
│       │   ├── __init__.py
│       │   ├── models.py          # Pydantic models
│       │   ├── definitions.yaml   # Concept definitions
│       │   └── registry.py        # Concept registry
│       ├── metrics/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── definitions.yaml
│       │   └── registry.py
│       ├── relationships/
│       │   ├── __init__.py
│       │   ├── graph.py           # NetworkX graph
│       │   └── join_paths.py      # Join path computation
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py            # DataAdapter Protocol
│       │   ├── duckdb.py          # DuckDB adapter
│       │   ├── postgres.py        # PostgreSQL adapter
│       │   └── snowflake.py       # Snowflake adapter
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py            # Provider abstraction
│       │   ├── openrouter.py      # OpenRouter (first-class)
│       │   ├── openai.py          # OpenAI provider
│       │   ├── anthropic.py       # Anthropic provider
│       │   ├── ollama.py          # Ollama provider
│       │   ├── llamacpp.py        # LlamaCpp provider
│       │   └── factory.py         # Provider factory
│       ├── scripts/
│       │   ├── __init__.py
│       │   ├── download_data.py   # UCI dataset download
│       │   └── build_warehouse.py # Kimball model build
│       ├── query_engine/
│       │   ├── __init__.py
│       │   ├── ir.py              # LQP dataclasses
│       │   ├── translator.py      # NL→LQP
│       │   ├── optimizer.py       # LQP optimization
│       │   ├── planner.py         # LQP→SQL
│       │   └── validator.py       # LQP validation
│       └── core/
│           ├── __init__.py
│           ├── ontology.py        # Main facade
│           ├── conversation.py    # Context management
│           └── tools.py           # Tool definitions
└── tests/
    ├── test_concepts.py
    ├── test_metrics.py
    ├── test_relationships.py
    ├── test_adapters.py
    ├── test_llm.py
    ├── test_query_engine.py
    └── test_core.py
```

## Development

```bash
# Run tests
uv run pytest packages/retail-ontology/tests -v

# Type check
uv run mypy packages/retail-ontology/src

# Lint
uv run ruff check packages/retail-ontology/src

# Format
uv run ruff format packages/retail-ontology/src

# Build
cd packages/retail-ontology && uv build
```

## Data Pipeline

The platform includes scripts to build a Kimball dimensional model from the UCI Online Retail dataset (ID 352):

1. **Download** - Fetches the dataset from UCI repository
2. **Transform** - Cleans and transforms to star schema:
   - `dim_customer` - Customer dimension
   - `dim_product` - Product dimension
   - `dim_date` - Date dimension
   - `fact_sale` - Sales fact table
3. **Load** - Creates DuckDB warehouse with proper indexes

```bash
# Run full pipeline
retail download && retail build

# Or programmatically
from retail_ontology.scripts import download_data, build_warehouse
download_data.main()
build_warehouse.main()
```

## License

MIT