# Variant 3: Headless Ontology Platform (Library/Skill Architecture)

## Overview
Core ontology + query engine packaged as a reusable Python library (`retail-ontology`) with thin interface adapters. Designed for embedding in other applications, distributing as a skill, or running as a headless service. OpenRouter is a first-class provider.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RETAIL ONTOLOGY PLATFORM (Headless)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RETAIL-ONTOLOGY CORE LIBRARY                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  Concepts   │  │  Metrics    │  │ Relationship│  │  Query    │  │   │
│  │  │  Registry   │  │  Registry   │  │  Graph      │  │  Engine   │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │   │
│  │         │                │                │                │         │   │
│  │         └────────────────┼────────────────┼────────────────┘         │   │
│  │                          ▼                ▼                          │   │
│  │                 ┌─────────────────────────────────┐                 │   │
│  │                 │      SEMANTIC LAYER (IR)        │                 │   │
│  │                 │  - Logical Query Plan (LQP)     │                 │   │
│  │                 │  - Optimization Rules           │                 │   │
│  │                 │  - Cost-based Planning          │                 │   │
│  │                 └──────────────┬──────────────────┘                 │   │
│  │                                │                                    │   │
│  │         ┌──────────────────────┼──────────────────────┐             │   │
│  │         ▼                      ▼                      ▼             │   │
│  │  ┌───────────┐          ┌───────────┐          ┌───────────┐       │   │
│  │  │  DuckDB   │          │  Postgres │          │  Snowflake│       │   │
│  │  │  Adapter  │          │  Adapter  │          │  (future) │  Adapter  │       │   │
│  │  └───────────┘          └───────────┘          └───────────┘       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐     │
│  │  CLI App    │           │ Telegram    │           │  REST API   │     │
│  │  (retail-cli)           │  Bot        │           │  (retail-api)│     │
│  │  thin wrapper           │  (retail-tg)│           │  thin wrapper│     │
│  └─────────────┘           └─────────────┘           └─────────────┘     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LLM PROVIDER ABSTRACTION                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ OpenAI   │ │Anthropic │ │ Ollama   │ │LlamaCpp  │ │OpenRouter│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────┬─────┘  │   │
│  │                                                            │         │   │
│  │  OpenRouter = Unified API for 100+ models                 │         │   │
│  │  (GPT-4, Claude, Llama, Mistral, Gemma, etc.)             │         │   │
│  └────────────────────────────────────────────────────────────┘         │   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
retail-ontology/                    # Core library (pip installable)
├── pyproject.toml
├── src/
│   └── retail_ontology/
│       ├── __init__.py
│       ├── concepts/
│       │   ├── registry.py
│       │   ├── definitions.yaml
│       │   └── models.py
│       ├── metrics/
│       │   ├── registry.py
│       │   ├── definitions.yaml
│       │   └── models.py
│       ├── relationships/
│       │   ├── graph.py
│       │   └── join_paths.py
│       ├── query_engine/
│       │   ├── translator.py       # NL → LQP (Logical Query Plan)
│       │   ├── optimizer.py        # Rule-based + cost-based
│       │   ├── planner.py          # LQP → Physical Plan
│       │   ├── validator.py        # Semantic validation
│       │   └── ir.py               # Intermediate Representation
│       ├── adapters/
│       │   ├── base.py             # Adapter interface
│       │   ├── duckdb.py
│       │   ├── postgres.py
│       │   └── snowflake.py        # Future
│       ├── llm/
│       │   ├── base.py
│       │   ├── openai.py
│       │   ├── anthropic.py
│       │   ├── ollama.py
│       │   ├── llamacpp.py
│       │   ├── openrouter.py       # FIRST-CLASS
│       │   └── factory.py
│       └── config.py               # Pydantic settings

retail-cli/                         # Thin CLI wrapper
├── pyproject.toml
└── src/retail_cli/
    ├── __main__.py
    ├── commands.py
    └── formatters.py

retail-telegram/                    # Thin Telegram wrapper
├── pyproject.toml
└── src/retail_telegram/
    ├── bot.py
    └── handlers.py

retail-api/                         # Thin FastAPI wrapper
├── pyproject.toml
└── src/retail_api/
    ├── main.py
    ├── routes.py
    └── dependencies.py
```

## Core Library API

```python
# retail_ontology/__init__.py
from retail_ontology import OntologyEngine, QueryResult

# Simple usage
engine = OntologyEngine.from_config("config.yaml")

# Ask a question
result: QueryResult = engine.ask("What was total revenue from UK in Dec 2011?")
print(result.answer)      # "£1,234,567.89"
print(result.sql)         # "SELECT SUM(line_total) FROM fact_sales..."
print(result.explanation) # "Joined fact_sales → dim_customer, filtered..."

# Advanced usage with conversation
session = engine.create_session()
session.ask("Top 5 products by revenue")
session.ask("And for UK only?")  # Context-aware
```

## OpenRouter Integration (First-Class)

```python
# retail_ontology/llm/openrouter.py
class OpenRouterProvider(LLMProvider):
    """
    OpenRouter provides unified access to 100+ models:
    - OpenAI: GPT-4o, GPT-4o-mini, o1-preview
    - Anthropic: Claude 3.5 Sonnet, Opus, Haiku
    - Meta: Llama 3.1 405B, 70B, 8B
    - Mistral: Large 2, Nemo, Codestral
    - Google: Gemma 2, Gemini
    - And many more...

    Benefits:
    - Single API key for all models
    - Automatic failover/fallback
    - Usage analytics across models
    - Competitive pricing (often cheaper than direct)
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini", **kwargs):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/yourorg/retail-ontology",
                "X-Title": "Retail Ontology Agent"
            }
        )
        self.model = model

    async def complete_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        # Use instructor with OpenRouter
        return await instructor.from_openai(self.client).chat.completions.create(
            model=self.model,
            response_model=schema,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
```

## Characteristics

| Aspect | Description |
|--------|-------------|
| **Deployment** | Library (`pip install retail-ontology`) + thin wrappers |
| **State** | Config-driven, adapters manage their own connections |
| **Scaling** | Library is stateless; adapters scale independently |
| **Latency** | In-process (library) + adapter overhead |
| **Development** | Library first, dogfood via thin wrappers |
| **Team** | Core team owns library; consumers own wrappers |
| **Extensibility** | Plugin system for adapters, LLM providers, metrics |

## Technology Stack
- **Core Library**: Pure Python, minimal deps (pydantic, pyyaml, networkx, instructor)
- **Adapters**: duckdb, psycopg2, snowflake-connector-python (optional deps)
- **LLM**: openai client (works for OpenRouter), ollama, llama-cpp-python
- **Distribution**: PyPI, uv, pipx for CLI tools
- **Testing**: pytest, hypothesis (property-based for query engine)

## Pros
- ✅ **True productization** - installable, versioned, reusable
- ✅ **Skill-ready** - natural fit for agent frameworks (LangChain, LlamaIndex, custom)
- ✅ **OpenRouter first-class** - 100+ models, single key, failover
- ✅ **Multi-database** - DuckDB for pilot, Postgres/Snowflake for prod
- ✅ **Thin wrappers** - CLI, Telegram, API, Web UI as separate packages
- ✅ **Embeddable** - use in notebooks, other apps, data pipelines
- ✅ **Clear boundaries** - ontology logic separated from interfaces
- ✅ **Monetizable** - core library can be commercial/enterprise

## Cons
- ❌ More upfront design work (stable APIs, versioning)
- ❌ Adapter pattern adds abstraction overhead
- ❌ Need to maintain multiple packages (or monorepo with publish pipeline)
- ❌ Library consumers may need migration guides
- ❌ Less control over deployment topology control (consumer decides)

## Best For
- **Long-term product vision** (skill, SaaS, embeddable library)
- **Multi-client deployments** (each client gets own adapter config)
- **OpenRouter-centric strategy** (model flexibility is key)
- **Team wants to dogfood library** via thin wrappers
- **Future: marketplace/skill distribution**

---

## Implementation Plan for Variant 3

### Phase 1: Core Library Foundation (Weeks 1-4)

#### Milestone 1.1: Monorepo Setup & Configuration (Week 1)

##### Tasks
- [ ] Create root `pyproject.toml` with uv workspace configuration
- [ ] Create `.python-version` (3.11+)
- [ ] Create `.env.example` with all configuration options
- [ ] Create `Makefile` with common commands
- [ ] Create `.gitignore` for monorepo
- [ ] Initialize git repository
- [ ] Set up pre-commit hooks (ruff, mypy)

##### Deliverables
- Working `uv sync` at root level
- All packages discoverable via `uv pip list`
- CI/CD pipeline skeleton (GitHub Actions)

#### Milestone 1.2: retail-ontology Core Package Structure (Week 1-2)

##### Tasks
- [ ] Create `packages/retail-ontology/pyproject.toml` with dependencies
- [ ] Create package directory structure (`src/retail_ontology/`)
- [ ] Implement `config.py` - Pydantic settings with environment variable support
- [ ] Implement `concepts/models.py` - Pydantic models for concept definitions
- [ ] Implement `concepts/definitions.yaml` - Business concepts (Customer, Product, Order, Sale)
- [ ] Implement `concepts/registry.py` - Concept registry with loading from YAML
- [ ] Implement `metrics/models.py` - Pydantic models for metric definitions
- [ ] Implement `metrics/definitions.yaml` - Metrics (Revenue, AOV, Repeat Rate, etc.)
- [ ] Implement `metrics/registry.py` - Metric registry with computation logic
- [ ] Implement `relationships/graph.py` - NetworkX graph for entity relationships
- [ ] Implement `relationships/join_paths.py` - Join path resolution

##### Configuration Schema (config.py)
```python
class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openrouter"  # openrouter, ollama, openai, anthropic, llamacpp
    llm_model: str = "openai/gpt-4o-mini"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    # Data
    duckdb_path: str = "./data/warehouse.duckdb"
    uci_dataset_id: int = 352

    # Adapters
    adapter_type: str = "duckdb"  # duckdb, postgres
    postgres_dsn: str | None = None

    # Telegram
    telegram_bot_token: str | None = None
    telegram_allowed_users: list[int] = []

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

##### Concept Definitions (definitions.yaml)
```yaml
concepts:
  customer:
    table: dim_customer
    primary_key: customer_key
    display_name: "Customer"
    attributes:
      - name: customer_key
        type: integer
        description: "Surrogate key"
      - name: customer_id
        type: string
        description: "Original customer ID from source"
      - name: country
        type: string
        description: "Customer country"

  product:
    table: dim_product
    primary_key: product_key
    display_name: "Product"
    attributes:
      - name: product_key
        type: integer
      - name: stock_code
        type: string
      - name: description
        type: string
      - name: unit_price
        type: decimal

  sale:
    table: fact_sales
    primary_key: sale_key
    display_name: "Sale"
    attributes:
      - name: sale_key
        type: integer
      - name: invoice_no
        type: string
      - name: invoice_date
        type: datetime
      - name: quantity
        type: integer
      - name: unit_price
        type: decimal
      - name: line_total
        type: decimal
      - name: customer_key
        type: integer
        foreign_key: dim_customer.customer_key
      - name: product_key
        type: integer
        foreign_key: dim_product.product_key
```

##### Metric Definitions (definitions.yaml)
```yaml
metrics:
  total_revenue:
    name: "Total Revenue"
    expression: "SUM(fact_sales.line_total)"
    grain: [customer_key, product_key, invoice_date]
    format: "currency"
    description: "Sum of all line totals"

  avg_order_value:
    name: "Average Order Value"
    expression: "AVG(order_total)"
    grain: [invoice_no]
    format: "currency"
    description: "Average revenue per invoice"
    dependencies:
      - order_total: "SUM(fact_sales.line_total) GROUP BY invoice_no"

  unique_customers:
    name: "Unique Customers"
    expression: "COUNT(DISTINCT dim_customer.customer_key)"
    grain: []
    format: "number"

  repeat_rate:
    name: "Repeat Customer Rate"
    expression: "repeat_customers / total_customers"
    grain: [invoice_date]
    format: "percentage"
    description: "Percentage of customers with >1 order"
```

#### Milestone 1.3: Data Layer - UCI Downloader & Warehouse Builder (Week 2)

##### Tasks
- [ ] Implement `scripts/download_data.py` - Download UCI dataset 352 via ucimlrepo
- [ ] Implement `scripts/build_warehouse.py` - ETL pipeline: raw → staging → dimensional model
- [ ] Create DuckDB schema (DDL) for dim_customer, dim_product, fact_sales
- [ ] Implement data cleaning (handle nulls, duplicates, negative quantities, returns)
- [ ] Implement Kimball dimensional modeling (surrogate keys, SCD Type 1)
- [ ] Add data validation checks (row counts, referential integrity, null checks)
- [ ] Create `retail_ontology/scripts/` module for CLI entry points

##### ETL Pipeline Steps
1. **Download**: `ucimlrepo.fetch_ucirepo(id=352)` → pandas DataFrame
2. **Validate**: Check schema, required columns, data types
3. **Clean**:
   - Remove rows with null CustomerID
   - Handle negative quantities (returns) - separate fact table or flag
   - Standardize country names
   - Parse dates
4. **Stage**: Write to staging tables in DuckDB
5. **Transform**: Build dimension tables (surrogate keys) and fact table
6. **Validate**: Row counts, FK integrity, sample queries

#### Milestone 1.4: Adapter Pattern - DuckDB Adapter (Week 3)

##### Tasks
- [ ] Define `adapters/base.py` - Adapter protocol/abstract base class
- [ ] Implement `adapters/duckdb.py` - DuckDB adapter with connection pooling
- [ ] Implement query execution with parameter binding
- [ ] Implement schema introspection (tables, columns, types)
- [ ] Add transaction support
- [ ] Add query result formatting (Polars DataFrame → list of dicts)

##### Adapter Protocol
```python
class DataAdapter(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def execute(self, sql: str, params: dict | None = None) -> QueryResult: ...
    async def execute_many(self, sql: str, params_list: list[dict]) -> None: ...
    async def fetch_schema(self) -> SchemaInfo: ...
    async def health_check(self) -> bool: ...

    # Context manager support
    async def __aenter__(self) -> "DataAdapter": ...
    async def __aexit__(self, *args) -> None: ...
```

#### Milestone 1.5: LLM Provider Abstraction (Week 3-4)

##### Tasks
- [ ] Define `llm/base.py` - LLMProvider abstract base class
- [ ] Implement `llm/openai.py` - OpenAI API provider
- [ ] Implement `llm/anthropic.py` - Anthropic API provider
- [ ] Implement `llm/ollama.py` - Ollama local provider
- [ ] Implement `llm/llamacpp.py` - llama.cpp local provider
- [ ] Implement `llm/openrouter.py` - **OpenRouter provider (first-class)**
- [ ] Implement `llm/factory.py` - Provider factory from config
- [ ] Add structured output support via instructor
- [ ] Add retry logic with tenacity
- [ ] Add token counting and cost estimation

##### OpenRouter Provider (Priority)
```python
class OpenRouterProvider(LLMProvider):
    """First-class OpenRouter support with model routing."""

    MODEL_TIERS = {
        "cheap": "openai/gpt-4o-mini",
        "balanced": "anthropic/claude-3.5-haiku",
        "premium": "openai/gpt-4o",
        "local_fallback": "ollama/llama3.1:8b",
    }

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini", **kwargs):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/yourorg/retail-ontology",
                "X-Title": "Retail Ontology Agent"
            }
        )
        self.model = model
        self.structured_client = instructor.from_openai(self.client)

    async def complete_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        return await self.structured_client.chat.completions.create(
            model=self.model,
            response_model=schema,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096,
        )

    async def complete_with_fallback(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        """Try primary model, fallback to cheaper/local on failure."""
        for tier in ["cheap", "balanced", "local_fallback"]:
            try:
                self.model = self.MODEL_TIERS[tier]
                return await self.complete_structured(prompt, schema)
            except Exception as e:
                logger.warning(f"Model {self.model} failed: {e}")
                continue
        raise RuntimeError("All models failed")
```

#### Milestone 1.6: CLI Wrapper - retail-cli (Week 4)

##### Tasks
- [ ] Create `packages/retail-cli/pyproject.toml`
- [ ] Implement `src/retail_cli/__main__.py` - Typer app with commands
- [ ] Implement `commands.py` - Command implementations
  - `ask` - Ask a question to the agent
  - `build` - Build warehouse
  - `download` - Download data
  - `config` - Show/validate configuration
  - `models` - List available LLM models
- [ ] Implement `formatters.py` - Rich output formatting (tables, panels, syntax highlighting)
- [ ] Add interactive REPL mode
- [ ] Add batch mode for testing

##### CLI Commands
```bash
# Interactive mode
retail ask "What was total revenue in Dec 2011?"

# Batch mode
retail ask "Top 5 products" --format json

# Data management
retail download
retail build

# Configuration
retail config show
retail config validate
retail models list
```

---

### Phase 2: Query Engine & Interfaces (Weeks 5-7)

#### Milestone 2.1: Query Engine - Intermediate Representation (Week 5)

##### Tasks
- [ ] Define `query_engine/ir.py` - Logical Query Plan (LQP) data structures
- [ ] Implement `query_engine/translator.py` - NL → LQP using LLM + ontology
- [ ] Implement `query_engine/optimizer.py` - Rule-based optimization
- [ ] Implement `query_engine/planner.py` - LQP → Physical Plan (SQL)
- [ ] Implement `query_engine/validator.py` - Semantic validation against ontology

##### Logical Query Plan (IR)
```python
@dataclass
class LogicalQueryPlan:
    # Core
    metrics: list[MetricRef]           # What to compute
    dimensions: list[DimensionRef]     # Group by what
    filters: list[FilterCondition]     # Where conditions
    grain: list[str]                   # Grain of the query

    # Derived
    required_tables: set[str]          # Tables needed
    required_joins: list[JoinPath]     # Join paths
    order_by: list[OrderBy] | None
    limit: int | None

    # Metadata
    confidence: float                  # 0-1
    explanation: str                   # Human-readable
    warnings: list[str]

@dataclass
class MetricRef:
    name: str                          # e.g., "total_revenue"
    alias: str | None = None

@dataclass
class DimensionRef:
    concept: str                       # e.g., "customer"
    attribute: str                     # e.g., "country"
    alias: str | None = None
```

#### Milestone 2.2: NL → Query Translation (Week 5-6)

##### Tasks
- [ ] Create few-shot prompts for query generation (`query_engine/prompts.py`)
- [ ] Implement structured output schema for LQP
- [ ] Add conversation context support
- [ ] Implement clarification handling (ambiguous questions)
- [ ] Add query validation against ontology registry
- [ ] Implement query explanation generation

##### Few-Shot Prompt Structure
```yaml
examples:
  - question: "Total revenue by country"
    lqp:
      metrics: ["total_revenue"]
      dimensions: [{concept: "customer", attribute: "country"}]
      filters: []

  - question: "Top 10 products by revenue in UK"
    lqp:
      metrics: ["total_revenue"]
      dimensions: [{concept: "product", attribute: "description"}]
      filters: [{concept: "customer", attribute: "country", operator: "=", value: "United Kingdom"}]
      order_by: [{metric: "total_revenue", direction: "desc"}]
      limit: 10

  - question: "Revenue trend over time"
    lqp:
      metrics: ["total_revenue"]
      dimensions: [{concept: "sale", attribute: "invoice_date", grain: "month"}]
      filters: []
```

#### Milestone 2.3: Agent Core Orchestration (Week 6)

##### Tasks
- [ ] Implement `core.py` - Main agent orchestration
- [ ] Implement `conversation.py` - Conversation history & context management
- [ ] Implement `tools.py` - Function calling tools for agent
- [ ] Integrate query engine with LLM provider
- [ ] Add error handling and retry logic
- [ ] Implement streaming response support

##### Agent Flow
```python
class OntologyAgent:
    def __init__(self, engine: OntologyEngine):
        self.engine = engine
        self.conversation = ConversationManager()

    async def ask(self, question: str) -> QueryResult:
        # 1. Add to conversation history
        self.conversation.add_user(question)

        # 2. Translate NL → LQP
        lqp = await self.engine.translate(question, self.conversation.context)

        # 3. Validate LQP
        validation = self.engine.validate(lqp)
        if not validation.valid:
            return QueryResult(error=validation.errors)

        # 4. Plan → Physical SQL
        sql = self.engine.plan(lqp)

        # 5. Execute
        data = await self.engine.execute(sql)

        # 6. Format answer
        answer = self.engine.format_answer(lqp, data)

        # 7. Add to conversation
        self.conversation.add_assistant(answer, sql=sql, lqp=lqp)

        return QueryResult(answer=answer, sql=sql, lqp=lqp, data=data)
```

#### Milestone 2.4: Telegram Wrapper - retail-telegram (Week 6-7)

##### Tasks
- [ ] Create `packages/retail-telegram/pyproject.toml`
- [ ] Implement `src/retail_telegram/bot.py` - Bot initialization
- [ ] Implement `handlers.py` - Command/message handlers
  - `/start` - Welcome message
  - `/help` - Help text
  - `/ask <question>` - Ask question
  - Inline query support
- [ ] Implement `middleware.py` - Auth, rate limiting, logging
- [ ] Add user session management
- [ ] Add markdown formatting for answers

#### Milestone 2.5: REST API Wrapper - retail-api (Week 7)

##### Tasks
- [ ] Create `packages/retail-api/pyproject.toml`
- [ ] Implement `src/retail_api/main.py` - FastAPI app
- [ ] Implement `routes.py` - API endpoints
  - `POST /ask` - Ask question
  - `POST /ask/stream` - Streaming answer
  - `GET /health` - Health check
  - `GET /concepts` - List concepts
  - `GET /metrics` - List metrics
  - `GET /schema` - Database schema
- [ ] Implement `dependencies.py` - Dependency injection (engine, auth)
- [ ] Implement `schemas.py` - Pydantic request/response models
- [ ] Add OpenAPI documentation
- [ ] Add authentication (API key / JWT)
- [ ] Add rate limiting

---

### Phase 3: Production Hardening (Weeks 8-10)

#### Milestone 3.1: Postgres Adapter (Week 8)

##### Tasks
- [ ] Implement `adapters/postgres.py` - Async Postgres adapter (asyncpg)
- [ ] Add connection pooling (asyncpg.Pool)
- [ ] Implement schema migration system (alembic)
- [ ] Add SSL/TLS support
- [ ] Implement read replica support
- [ ] Add query timeout and cancellation
- [ ] Test with DuckDB → Postgres parity

##### Migration Strategy
```python
# alembic/env.py
target_metadata = Base.metadata  # SQLAlchemy models

# migrations/versions/xxx_initial_schema.py
def upgrade():
    op.create_table('dim_customer', ...)
    op.create_table('dim_product', ...)
    op.create_table('fact_sales', ...)
    op.create_index('ix_fact_sales_customer_key', 'fact_sales', ['customer_key'])
    op.create_index('ix_fact_sales_product_key', 'fact_sales', ['product_key'])
    op.create_index('ix_fact_sales_invoice_date', 'fact_sales', ['invoice_date'])
```

#### Milestone 3.2: Testing & Quality (Week 8-9)

##### Tasks
- [ ] Unit tests for all core modules (concepts, metrics, relationships, query_engine)
- [ ] Integration tests for adapters (DuckDB, Postgres)
- [ ] Integration tests for LLM providers (mocked)
- [ ] E2E tests for CLI, Telegram, API
- [ ] Property-based tests for query engine (hypothesis)
- [ ] Performance benchmarks
- [ ] Load testing for API

##### Test Structure
```
tests/
├── unit/
│   ├── test_concepts.py
│   ├── test_metrics.py
│   ├── test_relationships.py
│   ├── test_query_engine/
│   │   ├── test_translator.py
│   │   ├── test_optimizer.py
│   │   ├── test_planner.py
│   │   └── test_validator.py
│   ├── test_adapters/
│   │   ├── test_duckdb.py
│   │   └── test_postgres.py
│   └── test_llm/
│       ├── test_openrouter.py
│       ├── test_ollama.py
│       └── test_factory.py
├── integration/
│   ├── test_e2e_query.py
│   ├── test_adapter_swap.py
│   ├── test_cli.py
│   ├── test_telegram.py
│   └── test_api.py
└── fixtures/
    └── sample_data.csv
```

#### Milestone 3.3: Documentation & Publishing (Week 9-10)

##### Tasks
- [ ] Write `docs/ontology_guide.md` - How to define concepts/metrics
- [ ] Write `docs/api.md` - REST API documentation
- [ ] Write `docs/deployment.md` - Deployment guides (Docker, K8s, serverless)
- [ ] Write `docs/architecture.md` - Updated architecture docs
- [ ] Create README for each package
- [ ] Set up PyPI publishing (GitHub Actions)
- [ ] Publish `retail-ontology` to PyPI
- [ ] Publish wrapper packages to PyPI
- [ ] Create example projects / notebooks

#### Milestone 3.4: Observability & Operations (Week 10)

##### Tasks
- [ ] Add structured logging (loguru) with correlation IDs
- [ ] Add metrics (Prometheus) - query latency, error rates, token usage
- [ ] Add tracing (OpenTelemetry) - LLM calls, DB queries, agent steps
- [ ] Add health check endpoints
- [ ] Create Docker images for each wrapper
- [ ] Create docker-compose for local development
- [ ] Document operational runbooks

---

### Detailed Task Breakdown by Week

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Monorepo + Config + Concepts/Metrics | Working uv workspace, config system, ontology definitions |
| 2 | Data Layer + DuckDB Adapter | UCI downloader, warehouse builder, DuckDB adapter |
| 3 | LLM Providers (OpenRouter first) | All providers working, factory, structured output |
| 4 | CLI Wrapper + Integration | `retail` CLI working end-to-end |
| 5 | Query Engine IR + Translator | NL → LQP working with few-shot prompts |
| 6 | Agent Core + Telegram | Agent orchestration, Telegram bot |
| 7 | REST API + Testing | FastAPI wrapper, test suite foundation |
| 8 | Postgres Adapter + Migrations | Production-ready adapter, alembic migrations |
| 9 | Testing + Documentation | Full test coverage, docs, PyPI publishing |
| 10 | Observability + Hardening | Logging, metrics, tracing, Docker, runbooks |

---

### Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenRouter API changes | Low | Medium | Pin versions, abstraction layer |
| NL → SQL accuracy | Medium | High | Extensive few-shot examples, validation, human-in-loop |
| DuckDB → Postgres parity | Medium | Medium | Comprehensive adapter tests, CI against both |
| Monorepo complexity | Low | Medium | Clear package boundaries, workspace scripts |
| LLM cost overruns | Medium | Low | Token counting, model tiers, caching |
| Scope creep | High | Medium | Strict milestone gates, defer non-core features |

---

### Success Criteria

#### Phase 1 Complete When:
- [ ] `uv sync` works at root
- [ ] `retail download && retail build` creates warehouse
- [ ] `retail ask "revenue by country"` returns correct answer
- [ ] All LLM providers work (OpenRouter, Ollama, OpenAI)
- [ ] Unit tests pass for concepts, metrics, adapters

#### Phase 2 Complete When:
- [ ] Complex questions work (filters, ordering, limits, time grains)
- [ ] Telegram bot responds to `/ask`
- [ ] REST API returns JSON answers
- [ ] Conversation context works (follow-up questions)
- [ ] Integration tests pass

#### Phase 3 Complete When:
- [ ] Postgres adapter passes all DuckDB tests
- [ ] Published to PyPI with version tags
- [ ] Documentation complete
- [ ] Observability stack working
- [ ] Load test: 100 req/s API, <500ms p99

---

### Next Immediate Steps

1. **Create monorepo structure** - Run the directory creation commands
2. **Set up root pyproject.toml** - Configure uv workspace
3. **Create retail-ontology package** - Start with config.py and concepts
4. **Implement UCI downloader** - Get real data flowing
5. **Build first DuckDB warehouse** - Validate dimensional model
6. **Wire up OpenRouter** - First LLM provider working
7. **First end-to-end CLI test** - "It works!" moment
