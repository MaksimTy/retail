# Retail Ontology Platform - Code Implementation Instructions

## Project Context
You are implementing **Variant 3: Headless Ontology Platform** - a reusable Python library (`retail-ontology`) with thin interface adapters (CLI, Telegram, REST API). This is a monorepo with multiple packages published to PyPI.

**Key Architecture Decisions:**
- **OpenRouter-first** LLM provider (100+ models, single API key, failover support)
- **DuckDB** for Phase 1 (local/dev), **Postgres** for Phase 3 (production)
- **Library-first** design: core logic in `retail-ontology`, thin wrappers in separate packages
- **Logical Query Plan (LQP)** as intermediate representation for NL→SQL translation

## Monorepo Structure
```
retail-ontology/          # Core library (pip installable)
├── pyproject.toml
└── src/retail_ontology/
    ├── concepts/         # Concept registry + YAML definitions
    ├── metrics/          # Metric registry + YAML definitions  
    ├── relationships/    # NetworkX graph + join paths
    ├── query_engine/     # NL→LQP→SQL pipeline
    ├── adapters/         # DuckDB, Postgres, Snowflake adapters
    ├── llm/              # Provider abstraction + OpenRouter (first-class)
    └── config.py         # Pydantic Settings

retail-cli/               # Thin Typer CLI wrapper
retail-telegram/          # Thin python-telegram-bot wrapper
retail-api/               # Thin FastAPI wrapper
```

## Implementation Phases (Follow Sequential Order)

### Phase 1: Core Library Foundation (Weeks 1-4)
**Priority Order:**
1. Monorepo setup: root `pyproject.toml` with uv workspace, `.python-version`, `.env.example`, `Makefile`, pre-commit
2. `retail-ontology` package structure + `config.py` (Pydantic Settings with all env vars)
3. Concepts: `models.py`, `definitions.yaml` (Customer, Product, Sale), `registry.py`
4. Metrics: `models.py`, `definitions.yaml` (Revenue, AOV, Repeat Rate, Unique Customers), `registry.py`
5. Relationships: `graph.py` (NetworkX), `join_paths.py`
6. Data layer: `scripts/download_data.py` (UCI dataset 352), `scripts/build_warehouse.py` (Kimball dimensional model)
7. DuckDB Adapter: `adapters/base.py` (Protocol), `adapters/duckdb.py` (connection pooling, schema introspection)
8. LLM Providers: `llm/base.py`, `llm/openrouter.py` (FIRST-CLASS with fallback tiers), `llm/factory.py`, + OpenAI, Anthropic, Ollama, LlamaCpp
9. CLI Wrapper: `retail-cli` with `ask`, `build`, `download`, `config`, `models` commands + Rich formatting

### Phase 2: Query Engine & Interfaces (Weeks 5-7)
1. Query Engine IR: `ir.py` (LQP dataclasses), `translator.py` (NL→LQP via few-shot LLM), `optimizer.py`, `planner.py` (LQP→SQL), `validator.py`
2. Agent Core: `core.py` (orchestration), `conversation.py` (context management), `tools.py`
3. Telegram Wrapper: `retail-telegram` with `/ask`, inline queries, sessions
4. REST API Wrapper: `retail-api` with FastAPI, `/ask`, `/ask/stream`, `/health`, `/concepts`, `/metrics`, `/schema`, auth, rate limiting

### Phase 3: Production Hardening (Weeks 8-10)
1. Postgres Adapter: `adapters/postgres.py` (asyncpg), Alembic migrations, SSL, read replicas
2. Testing: Unit (all modules), Integration (adapters, LLM providers), E2E (CLI, Telegram, API), Property-based (hypothesis)
3. Documentation: `docs/ontology_guide.md`, `docs/api.md`, `docs/deployment.md`, package READMEs
4. PyPI Publishing: GitHub Actions workflows for all packages
5. Observability: Structured logging (loguru), Prometheus metrics, OpenTelemetry tracing, Docker images, docker-compose

## Critical Implementation Details

### OpenRouter Provider (MUST BE FIRST-CLASS)
```python
# llm/openrouter.py - Key requirements:
- Base URL: https://openrouter.ai/api/v1
- Default headers: HTTP-Referer, X-Title
- Model tiers: cheap (gpt-4o-mini), balanced (claude-3.5-haiku), premium (gpt-4o), local_fallback (ollama/llama3.1:8b)
- Fallback logic: try tiers in order on failure
- Structured output via instructor
- Token counting + cost estimation
```

### Configuration Schema (config.py)
```python
class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openrouter"
    llm_model: str = "openai/gpt-4o-mini"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    # Data
    duckdb_path: str = "./data/warehouse.duckdb"
    uci_dataset_id: int = 352
    
    # Adapters
    adapter_type: str = "duckdb"
    postgres_dsn: str | None = None
    
    # Telegram
    telegram_bot_token: str | None = None
    telegram_allowed_users: list[int] = []
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
```

### Concept/Metric Definitions (YAML)
- Concepts: `dim_customer`, `dim_product`, `fact_sales` with attributes, PKs, FKs
- Metrics: `total_revenue`, `avg_order_value`, `unique_customers`, `repeat_rate` with expressions, grain, format

### Adapter Protocol
```python
class DataAdapter(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def execute(self, sql: str, params: dict | None = None) -> QueryResult: ...
    async def execute_many(self, sql: str, params_list: list[dict]) -> None: ...
    async def fetch_schema(self) -> SchemaInfo: ...
    async def health_check(self) -> bool: ...
    async def __aenter__(self) -> "DataAdapter": ...
    async def __aexit__(self, *args) -> None: ...
```

### Query Engine Flow
```
NL Question → Translator (LLM + few-shot) → LQP → Validator → Planner → SQL → Adapter → Data → Formatter → Answer
```

## Code Quality Standards
- **Type hints everywhere** (strict mypy)
- **Async/await** for all I/O (adapters, LLM, HTTP)
- **Pydantic v2** for all data models and settings
- **Structured logging** (loguru) with correlation IDs
- **Error handling**: Custom exceptions, retry logic (tenacity), graceful degradation
- **Testing**: pytest + hypothesis for query engine, mocked LLM providers
- **Documentation**: Docstrings for all public APIs, README per package

## Key Dependencies
- Core: `pydantic`, `pydantic-settings`, `pyyaml`, `networkx`, `instructor`, `openai` (for OpenRouter)
- Adapters: `duckdb`, `psycopg2`/`asyncpg`, `snowflake-connector-python` (optional)
- CLI: `typer`, `rich`
- Telegram: `python-telegram-bot`
- API: `fastapi`, `uvicorn`, `pydantic`
- Testing: `pytest`, `hypothesis`, `pytest-asyncio`
- Observability: `loguru`, `prometheus-client`, `opentelemetry`

## Immediate Next Steps (Start Here)
1. Create monorepo directory structure
2. Write root `pyproject.toml` with uv workspace config
3. Create `retail-ontology/pyproject.toml` with dependencies
4. Implement `config.py` with full Settings class
5. Implement concepts/models.py + definitions.yaml + registry.py
6. Implement metrics/models.py + definitions.yaml + registry.py

## Success Criteria for Phase 1
- `uv sync` works at root level
- `retail download && retail build` creates valid DuckDB warehouse
- `retail ask "revenue by country"` returns correct answer via OpenRouter
- All LLM providers instantiate via factory
- Unit tests pass for concepts, metrics, adapters

---

**Reference Files:**
- Full architecture: `plans/VARIANT_3_HEADLESS_LIBRARY.md`
- Project overview: `README.md`

**Implementation Approach:** Work sequentially through milestones. Complete each milestone fully before moving to the next. Prioritize OpenRouter integration and DuckDB adapter as they're the critical path for end-to-end validation.