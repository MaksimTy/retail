---
name: retail-ontology-platform
description: Implement the Retail Ontology Platform (Variant 3: Headless Ontology Platform) - a reusable Python library (retail-ontology) with thin interface adapters (CLI, Telegram, REST API). This skill guides sequential implementation through three phases: Core Library Foundation, Query Engine & Interfaces, and Production Hardening. Use when building or extending the monorepo with OpenRouter-first LLM provider, DuckDB/Postgres adapters, Logical Query Plan (LQP) for NL→SQL translation, and library-first architecture.
---

# Retail Ontology Platform Implementation Skill

## When to use this skill
- Implementing the Retail Ontology Platform monorepo from scratch
- Adding new packages (retail-ontology, retail-cli, retail-telegram, retail-api)
- Building core library components: concepts, metrics, relationships, query engine, adapters, LLM providers
- Implementing Phase 1 (Core Library), Phase 2 (Query Engine & Interfaces), or Phase 3 (Production Hardening)
- Setting up monorepo tooling (uv workspace, pre-commit, Makefile, PyPI publishing)

## When NOT to use this skill
- Working on unrelated Python projects without the Retail Ontology architecture
- Quick prototyping without following the phased implementation approach
- Projects that don't use OpenRouter, DuckDB, or the LQP-based NL→SQL pipeline

## Inputs required from the user
- Target phase/milestone to implement (Phase 1, 2, or 3)
- Specific component within the phase (e.g., "concepts registry", "OpenRouter provider", "DuckDB adapter")
- Any environment-specific configuration (API keys, database paths, etc.)

## Workflow

### Phase 1: Core Library Foundation (Weeks 1-4)
1. **Monorepo Setup**
   - Create root `pyproject.toml` with uv workspace configuration
   - Add `.python-version`, `.env.example`, `Makefile`, pre-commit hooks
   - Verify: `uv sync` works at root level

2. **Core Package Structure** (`retail-ontology/`)
   - Create `retail-ontology/pyproject.toml` with dependencies
   - Implement `config.py` with full Pydantic Settings class (see Configuration Schema in references/config_schema.md)
   - Set up `src/retail_ontology/` package structure

3. **Concepts Module**
   - `models.py` - Pydantic models for concepts
   - `definitions.yaml` - Customer, Product, Sale definitions with attributes, PKs, FKs
   - `registry.py` - Concept registry with YAML loading

4. **Metrics Module**
   - `models.py` - Pydantic models for metrics
   - `definitions.yaml` - Revenue, AOV, Repeat Rate, Unique Customers with expressions, grain, format
   - `registry.py` - Metric registry with YAML loading

5. **Relationships Module**
   - `graph.py` - NetworkX graph for join paths
   - `join_paths.py` - Join path computation and validation

6. **Data Layer Scripts**
   - `scripts/download_data.py` - UCI dataset 352 download
   - `scripts/build_warehouse.py` - Kimball dimensional model build

7. **DuckDB Adapter**
   - `adapters/base.py` - DataAdapter Protocol (see references/adapter_protocol.md)
   - `adapters/duckdb.py` - Connection pooling, schema introspection

8. **LLM Providers**
   - `llm/base.py` - Provider abstraction
   - `llm/openrouter.py` - **FIRST-CLASS** OpenRouter implementation (see references/openrouter.md)
   - `llm/factory.py` - Provider factory
   - Additional providers: OpenAI, Anthropic, Ollama, LlamaCpp

9. **CLI Wrapper** (`retail-cli/`)
   - Typer-based CLI with `ask`, `build`, `download`, `config`, `models` commands
   - Rich formatting for output

**Phase 1 Success Criteria:**
- `uv sync` works at root level
- `retail download && retail build` creates valid DuckDB warehouse
- `retail ask "revenue by country"` returns correct answer via OpenRouter
- All LLM providers instantiate via factory
- Unit tests pass for concepts, metrics, adapters

### Phase 2: Query Engine & Interfaces (Weeks 5-7)
1. **Query Engine IR**
   - `ir.py` - LQP dataclasses (Logical Query Plan)
   - `translator.py` - NL→LQP via few-shot LLM
   - `optimizer.py` - LQP optimization
   - `planner.py` - LQP→SQL translation
   - `validator.py` - LQP validation

2. **Agent Core**
   - `core.py` - Orchestration logic
   - `conversation.py` - Context management
   - `tools.py` - Tool definitions

3. **Telegram Wrapper** (`retail-telegram/`)
   - python-telegram-bot wrapper with `/ask`, inline queries, sessions

4. **REST API Wrapper** (`retail-api/`)
   - FastAPI with `/ask`, `/ask/stream`, `/health`, `/concepts`, `/metrics`, `/schema`
   - Auth, rate limiting

### Phase 3: Production Hardening (Weeks 8-10)
1. **Postgres Adapter**
   - `adapters/postgres.py` - asyncpg implementation
   - Alembic migrations, SSL, read replicas

2. **Testing**
   - Unit tests (all modules)
   - Integration tests (adapters, LLM providers)
   - E2E tests (CLI, Telegram, API)
   - Property-based tests (hypothesis)

3. **Documentation**
   - `docs/ontology_guide.md`, `docs/api.md`, `docs/deployment.md`
   - Package READMEs

4. **PyPI Publishing**
   - GitHub Actions workflows for all packages

5. **Observability**
   - Structured logging (loguru)
   - Prometheus metrics
   - OpenTelemetry tracing
   - Docker images, docker-compose

## Code Quality Standards (Enforce Throughout)
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

## Examples

### Example: Starting Phase 1 Monorepo Setup
```
User: "Set up the monorepo structure for Retail Ontology Platform"
Agent: Creates root pyproject.toml with uv workspace, .python-version, .env.example, Makefile, pre-commit
```

### Example: Implementing OpenRouter Provider
```
User: "Implement the OpenRouter LLM provider as first-class citizen"
Agent: Creates llm/openrouter.py with fallback tiers, structured output via instructor, token counting
```

### Example: Building DuckDB Warehouse
```
User: "Run the data download and warehouse build"
Agent: Executes retail download && retail build, verifies DuckDB warehouse creation
```

## Troubleshooting / Edge Cases

| Issue | Resolution |
|-------|------------|
| `uv sync` fails | Check Python version matches `.python-version`, verify pyproject.toml syntax |
| OpenRouter API errors | Verify API key in `.env`, check model tier availability, review fallback logic |
| DuckDB connection issues | Ensure `duckdb_path` directory exists, check file permissions |
| LQP validation fails | Review few-shot examples in translator, check concept/metric definitions |
| Import errors in monorepo | Verify uv workspace configuration, check package pyproject.toml dependencies |

## References
- [Configuration Schema](references/config_schema.md) - Full Pydantic Settings class
- [Adapter Protocol](references/adapter_protocol.md) - DataAdapter Protocol definition
- [OpenRouter Provider](references/openrouter.md) - OpenRouter implementation details
- [Full Architecture Plan](plans/VARIANT_3_HEADLESS_LIBRARY.md) - Complete architecture documentation
- [Project Overview](README.md) - High-level project description
