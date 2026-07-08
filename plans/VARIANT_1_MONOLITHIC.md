# Variant 1: Monolithic Embedded Architecture (Current Baseline)

## Overview
Single-process Python application with embedded DuckDB. All layers (Data, Ontology, Agent, Interface) run in one process. This is the architecture currently documented in `ARCHITECTURE.md` and `PROJECT_STRUCTURE.md`.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETAIL AI AGENT (Monolith)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │   CLI    │  │ Telegram │  │  REST    │  │   Web UI     │   │
│  │  (Typer) │  │  (PTB)   │  │ (FastAPI)│  │  (Streamlit) │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       │             │             │             │             │
│       └─────────────┼─────────────┼─────────────┘             │
│                     ▼             ▼                           │
│            ┌─────────────────────────────┐                    │
│            │        AGENT CORE           │                    │
│            │  (Orchestration + Tools)    │                    │
│            └──────────────┬──────────────┘                    │
│                           │                                    │
│            ┌──────────────┴──────────────┐                    │
│            │      ONTOLOGY LAYER         │                    │
│            │  (Concepts, Metrics, Graph, │                    │
│            │   Query Builder, Validator) │                    │
│            └──────────────┬──────────────┘                    │
│                           │                                    │
│            ┌──────────────┴──────────────┐                    │
│            │       DATA LAYER            │                    │
│            │  (DuckDB + SQLAlchemy +     │                    │
│            │   Polars ETL + ucimlrepo)   │                    │
│            └──────────────┬──────────────┘                    │
│                           │                                    │
│            ┌──────────────┴──────────────┐                    │
│            │      LLM PROVIDERS          │                    │
│            │  (OpenAI, Anthropic, Ollama,│                    │
│            │   LlamaCpp, vLLM, OpenRouter)                    │
│            └─────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Characteristics

| Aspect | Description |
|--------|-------------|
| **Deployment** | Single binary/container, `uv run retail` |
| **State** | Embedded DuckDB file (`./data/warehouse.duckdb`) |
| **Scaling** | Vertical only (single process) |
| **Latency** | Minimal (in-process calls, no network hops) |
| **Development** | Simple, fast iteration, easy debugging |
| **Team** | Single developer or small team |
| **Extensibility** | Plugin system for LLM providers, interfaces |

## Technology Stack
- **Core**: Python 3.11+, uv, pydantic, pydantic-settings
- **Data**: DuckDB, Polars, SQLAlchemy 2.0, ucimlrepo
- **Ontology**: PyYAML, NetworkX, instructor (structured output)
- **Agent**: Custom orchestration, tenacity (retries)
- **Interfaces**: Typer (CLI), python-telegram-bot v20, FastAPI, Streamlit
- **LLM**: openai, anthropic, ollama, llama-cpp-python, vllm, openai (for OpenRouter)

## Pros
- ✅ Simplest deployment (single file/container)
- ✅ Lowest latency (no IPC/network)
- ✅ Easiest to develop, test, debug
- ✅ Perfect for pilot/demo/PoC
- ✅ Zero infrastructure dependencies
- ✅ Natural fit for "skill" packaging later

## Cons
- ❌ Single point of failure
- ❌ Cannot scale components independently
- ❌ All interfaces share same process resources
- ❌ Harder to swap data layer (e.g., to Postgres/Snowflake)
- ❌ LLM provider failures can crash main process

## Best For
- Pilot project / demo / PoC
- Single developer or small team
- Local development and testing
- Embedding as a library/skill later

---

## Implementation Plan for Variant 1

### Phase 1: Foundation (Week 1)

#### Milestone 1.1: Project Setup & Configuration
- [ ] Update root `pyproject.toml` with all dependencies
- [ ] Create `src/retail/config/settings.py` - Pydantic BaseSettings
- [ ] Create `src/retail/config/logging.py` - Loguru setup
- [ ] Create `.env.example` with all configuration options
- [ ] Create `Makefile` with common commands
- [ ] Set up pre-commit (ruff, mypy)

#### Milestone 1.2: Data Layer - UCI Downloader & Validators
- [ ] Create `src/retail/data/source/uci_downloader.py`
- [ ] Create `src/retail/data/source/validators.py`
- [ ] Implement UCI dataset 352 download via ucimlrepo
- [ ] Add raw data validation (schema, nulls, types)
- [ ] Add anomaly detection (negative quantities, future dates, etc.)

#### Milestone 1.3: Data Layer - Staging & Cleaning
- [ ] Create `src/retail/data/staging/cleaner.py`
- [ ] Implement cleaning rules:
  - Remove rows with null CustomerID
  - Handle negative quantities (returns) - flag or separate
  - Standardize country names
  - Parse invoice dates
  - Remove duplicates
  - Validate price > 0
- [ ] Write cleaned data to staging tables

#### Milestone 1.4: Data Layer - Warehouse Models & Schema
- [ ] Create `src/retail/data/warehouse/models.py` - SQLAlchemy ORM models
- [ ] Create `src/retail/data/warehouse/schema.py` - DDL for DuckDB
- [ ] Define dimensional model:
  - `dim_customer` (customer_key PK, customer_id, country)
  - `dim_product` (product_key PK, stock_code, description, unit_price)
  - `fact_sales` (sale_key PK, customer_key FK, product_key FK, invoice_no, invoice_date, quantity, unit_price, line_total)

#### Milestone 1.5: Data Layer - ETL Loader
- [ ] Create `src/retail/data/warehouse/loader.py`
- [ ] Implement Kimball ETL:
  1. Load dimensions (customers, products) with surrogate keys
  2. Load fact table with FK lookups
  3. Compute line_total = quantity * unit_price
  4. Handle SCD Type 1 for dimensions
- [ ] Add data quality checks (row counts, FK integrity)
- [ ] Create `retail.deployment.scripts.build_warehouse` entry point

---

### Phase 2: Ontology Layer (Week 2)

#### Milestone 2.1: Concepts & Metrics Definitions
- [ ] Create `src/retail/ontology/concepts/definitions.yaml`
- [ ] Create `src/retail/ontology/metrics/definitions.yaml`
- [ ] Create `src/retail/ontology/concepts/registry.py`
- [ ] Create `src/retail/ontology/metrics/registry.py`
- [ ] Create `src/retail/ontology/relationships/graph.py`

#### Milestone 2.2: Query Builder - Translator & Prompts
- [ ] Create `src/retail/ontology/query_builder/prompts.py` - Few-shot prompts
- [ ] Create `src/retail/ontology/query_builder/translator.py` - NL → SQL
- [ ] Create `src/retail/ontology/query_builder/validator.py` - Query validation
- [ ] Implement structured output schema for SQL generation

#### Few-Shot Prompts Example
```python
FEW_SHOT_EXAMPLES = [
    {
        "question": "Total revenue by country",
        "sql": "SELECT c.country, SUM(f.line_total) as total_revenue FROM fact_sales f JOIN dim_customer c ON f.customer_key = c.customer_key GROUP BY c.country ORDER BY total_revenue DESC"
    },
    {
        "question": "Top 10 products by revenue in UK",
        "sql": "SELECT p.description, SUM(f.line_total) as revenue FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key JOIN dim_customer c ON f.customer_key = c.customer_key WHERE c.country = 'United Kingdom' GROUP BY p.description ORDER BY revenue DESC LIMIT 10"
    },
    {
        "question": "Monthly revenue trend for 2011",
        "sql": "SELECT DATE_TRUNC('month', invoice_date) as month, SUM(line_total) as revenue FROM fact_sales WHERE invoice_date >= '2011-01-01' AND invoice_date < '2012-01-01' GROUP BY month ORDER BY month"
    },
]
```

---

### Phase 3: Agent Layer (Week 3)

#### Milestone 3.1: LLM Provider Abstraction
- [ ] Create `src/retail/agent/llm/base.py` - Abstract LLMProvider
- [ ] Create `src/retail/agent/llm/openai.py`
- [ ] Create `src/retail/agent/llm/anthropic.py`
- [ ] Create `src/retail/agent/llm/ollama.py`
- [ ] Create `src/retail/agent/llm/llamacpp.py`
- [ ] Create `src/retail/agent/llm/openrouter.py` - **OpenRouter support**
- [ ] Create `src/retail/agent/llm/factory.py` - Provider factory

#### Milestone 3.2: Agent Core & Conversation
- [ ] Create `src/retail/agent/core.py` - Main orchestration
- [ ] Create `src/retail/agent/conversation.py` - Context management
- [ ] Create `src/retail/agent/tools.py` - Function calling tools
- [ ] Implement NL → Query → Execute → Answer pipeline

#### Agent Core Implementation
```python
class OntologyAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = create_llm_provider(settings)
        self.query_builder = QueryBuilder(settings)
        self.repository = DataRepository(settings)
        self.conversation = ConversationManager()

    async def ask(self, question: str) -> AgentResponse:
        # 1. Build context from conversation
        context = self.conversation.get_context()

        # 2. Translate NL to SQL
        sql = await self.query_builder.translate(question, context)

        # 3. Validate SQL
        if not self.query_builder.validate(sql):
            return AgentResponse(error="Invalid query generated")

        # 4. Execute
        results = await self.repository.execute(sql)

        # 5. Format answer
        answer = self.format_answer(question, sql, results)

        # 6. Update conversation
        self.conversation.add(question, answer, sql)

        return AgentResponse(answer=answer, sql=sql, data=results)
```

---

### Phase 4: Interfaces (Week 4)

#### Milestone 4.1: CLI Interface
- [ ] Create `src/retail/interfaces/cli/app.py` - Typer app
- [ ] Create `src/retail/interfaces/cli/commands.py` - Commands
- [ ] Create `src/retail/interfaces/cli/formatters.py` - Rich formatting
- [ ] Create `src/retail/__main__.py` - Entry point

#### CLI Commands
```bash
retail ask "What was total revenue in Dec 2011?"
retail ask "Top 5 products" --format table
retail download
retail build
retail config show
```

#### Milestone 4.2: Telegram Bot
- [ ] Create `src/retail/interfaces/telegram/bot.py`
- [ ] Create `src/retail/interfaces/telegram/handlers.py`
- [ ] Create `src/retail/interfaces/telegram/middleware.py`
- [ ] Implement `/start`, `/help`, `/ask` commands
- [ ] Add inline query support
- [ ] Add user authorization

#### Milestone 4.3: Deployment Scripts
- [ ] Create `src/retail/deployment/scripts/download_data.py`
- [ ] Create `src/retail/deployment/scripts/build_warehouse.py`
- [ ] Create `src/retail/deployment/scripts/setup.sh`
- [ ] Create `src/retail/deployment/docker/Dockerfile`
- [ ] Create `src/retail/deployment/docker/docker-compose.yml`

---

### Phase 5: Testing & Hardening (Week 5-6)

#### Milestone 5.1: Testing
- [ ] Unit tests for all modules
- [ ] Integration tests for E2E flow
- [ ] Test fixtures with sample data
- [ ] Property-based tests for query generation

#### Milestone 5.2: Documentation
- [ ] Update README.md
- [ ] Create docs/architecture.md
- [ ] Create docs/deployment.md
- [ ] Create docs/ontology_guide.md

---

### Detailed Task Breakdown by Week

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Config + Data Layer (download, clean, warehouse) | Working ETL, DuckDB populated |
| 2 | Ontology Layer (concepts, metrics, query builder) | NL → SQL working for basic queries |
| 3 | Agent Layer (LLM providers, orchestration) | Agent answers questions end-to-end |
| 4 | Interfaces (CLI, Telegram) | `retail ask` and Telegram bot working |
| 5 | Testing + Polish | Test coverage, bug fixes |
| 6 | Documentation + Deploy | Docs, Docker, release |

---

### Success Criteria
- [ ] `uv run retail download && uv run retail build` creates warehouse
- [ ] `uv run retail ask "revenue by country"` returns correct answer
- [ ] Telegram bot responds to `/ask` commands
- [ ] All LLM providers work (OpenRouter, Ollama, OpenAI, Anthropic)
- [ ] Complex queries work (filters, joins, aggregations, time grains)
- [ ] Conversation context works (follow-up questions)
- [ ] Test coverage > 80%
- [ ] Docker image builds and runs

---

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| NL → SQL accuracy | Extensive few-shot examples, validation, iterative refinement |
| LLM cost | Token counting, model selection, caching |
| DuckDB performance | Proper indexing, partitioning for larger datasets |
| Scope creep | Strict milestone gates, defer non-core features |

---

### Next Immediate Steps
1. Update root `pyproject.toml` with all dependencies
2. Create config/settings.py with Pydantic
3. Implement UCI downloader
4. Build first DuckDB warehouse
5. Wire up OpenRouter provider
6. First end-to-end test: `retail ask "total revenue"`
