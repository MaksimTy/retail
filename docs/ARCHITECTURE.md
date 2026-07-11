# Architecture Documentation

## Retail Ontology Platform - Headless Library Architecture

### Overview

The Retail Ontology Platform is a headless, library-first architecture designed for retail analytics. It provides a reusable Python library (`retail-ontology`) with thin interface adapters for multiple deployment targets.

### Architecture Diagram

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

### Package Structure

```
retail-ontology-platform/
├── packages/
│   ├── retail-ontology/     # Core library (pip installable)
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/retail_ontology/
│   │       ├── __init__.py
│   │       ├── config.py               # Pydantic settings with environment variable support
│   │       ├── concepts/
│   │       │   ├── registry.py         # Concept registry with loading from YAML
│   │       │   ├── definitions.yaml    # Business concepts (Customer, Product, Order, Sale)
│   │       │   └── models.py           # Pydantic models for concept definitions
│   │       ├── metrics/
│   │       │   ├── registry.py         # Metric registry with computation logic
│   │       │   ├── definitions.yaml    # Metrics (Revenue, AOV, Repeat Rate, etc.)
│   │       │   └── models.py           # Pydantic models for metric definitions
│   │       ├── relationships/
│   │       │   ├── graph.py            # NetworkX graph for entity relationships
│   │       │   └── join_paths.py       # Join path resolution
│   │       ├── query_engine/
│   │       │   ├── translator.py       # NL → LQP (Logical Query Plan)
│   │       │   ├── optimizer.py        # Rule-based + cost-based optimization
│   │       │   ├── planner.py          # LQP → Physical Plan
│   │       │   ├── validator.py        # Semantic validation
│   │       │   └── ir.py               # Intermediate Representation
│   │       ├── adapters/
│   │       │   ├── base.py             # Adapter interface
│   │       │   ├── duckdb.py           # DuckDB adapter
│   │       │   ├── postgres.py         # PostgreSQL adapter
│   │       │   └── snowflake.py        # Future: Snowflake adapter
│   │       ├── llm/
│   │       │   ├── base.py             # LLMProvider abstract base class
│   │       │   ├── openai.py           # OpenAI API provider
│   │       │   ├── anthropic.py        # Anthropic API provider
│   │       │   ├── ollama.py           # Ollama local provider
│   │       │   ├── llamacpp.py         # llama.cpp local provider
│   │       │   ├── openrouter.py       # OpenRouter provider (first-class)
│   │       │   └── factory.py          # Provider factory from config
│   │       └── scripts/
│   │           ├── download_data.py    # UCI dataset download
│   │           └── build_warehouse.py  # Kimball model build
│   ├── retail-cli/          # Thin CLI wrapper
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/retail_cli/
│   │       ├── __main__.py
│   │       ├── commands.py
│   │       └── formatters.py
│   ├── retail-telegram/     # Thin Telegram wrapper
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/retail_telegram/
│   │       ├── bot.py
│   │       └── handlers.py
│   └── retail-api/          # Thin FastAPI wrapper
│       ├── pyproject.toml
│       ├── README.md
│       └── src/retail_api/
│           ├── main.py
│           ├── routes.py
│           └── dependencies.py
├── pyproject.toml           # Root workspace config
├── Makefile                   # Development commands
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .env.example               # Environment variables template
└── .python-version            # Python version (3.11)
```

### Core Components

#### 1. Concepts Registry

The Concepts Registry defines business entities (dimensions) with their attributes, primary keys, and foreign keys.

**Key Files:**
- [`concepts/models.py`](packages/retail-ontology/src/retail_ontology/concepts/models.py) - Pydantic models for concept definitions
- [`concepts/definitions.yaml`](packages/retail-ontology/src/retail_ontology/concepts/definitions.yaml) - Concept definitions
- [`concepts/registry.py`](packages/retail-ontology/src/retail_ontology/concepts/registry.py) - Concept registry

#### 2. Metrics Registry

The Metrics Registry defines business metrics with expressions, grain, and formatting rules.

**Key Files:**
- [`metrics/models.py`](packages/retail-ontology/src/retail_ontology/metrics/models.py) - Pydantic models for metric definitions
- [`metrics/definitions.yaml`](packages/retail-ontology/src/retail_ontology/metrics/definitions.yaml) - Metric definitions
- [`metrics/registry.py`](packages/retail-ontology/src/retail_ontology/metrics/registry.py) - Metric registry

#### 3. Relationships Graph

The Relationships Graph uses NetworkX to compute and validate join paths between entities.

**Key Files:**
- [`relationships/graph.py`](packages/retail-ontology/src/retail_ontology/relationships/graph.py) - NetworkX graph implementation
- [`relationships/join_paths.py`](packages/retail-ontology/src/retail_ontology/relationships/join_paths.py) - Join path resolution

#### 4. Query Engine

The Query Engine translates natural language questions to SQL through a multi-stage pipeline:

1. **NL → LQP**: Natural language to Logical Query Plan
2. **LQP Optimization**: Rule-based and cost-based optimization
3. **LQP → SQL**: Physical plan generation
4. **Validation**: Semantic validation against ontology

**Key Files:**
- [`query_engine/ir.py`](packages/retail-ontology/src/retail_ontology/query_engine/ir.py) - Logical Query Plan data structures
- [`query_engine/translator.py`](packages/retail-ontology/src/retail_ontology/query_engine/translator.py) - NL → LQP translation
- [`query_engine/optimizer.py`](packages/retail-ontology/src/retail_ontology/query_engine/optimizer.py) - LQP optimization
- [`query_engine/planner.py`](packages/retail-ontology/src/retail_ontology/query_engine/planner.py) - LQP → SQL planning
- [`query_engine/validator.py`](packages/retail-ontology/src/retail_ontology/query_engine/validator.py) - LQP validation

#### 5. Data Adapters

Data Adapters provide a unified interface for different database backends.

**Adapter Protocol:**
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

**Key Files:**
- [`adapters/base.py`](packages/retail-ontology/src/retail_ontology/adapters/base.py) - Adapter protocol
- [`adapters/duckdb.py`](packages/retail-ontology/src/retail_ontology/adapters/duckdb.py) - DuckDB adapter
- [`adapters/postgres.py`](packages/retail-ontology/src/retail_ontology/adapters/postgres.py) - PostgreSQL adapter

#### 6. LLM Providers

LLM Providers abstract the LLM API interactions with support for multiple providers.

**Key Files:**
- [`llm/base.py`](packages/retail-ontology/src/retail_ontology/llm/base.py) - Provider abstraction
- [`llm/openrouter.py`](packages/retail-ontology/src/retail_ontology/llm/openrouter.py) - OpenRouter provider (first-class)
- [`llm/factory.py`](packages/retail-ontology/src/retail_ontology/llm/factory.py) - Provider factory

### OpenRouter Integration

OpenRouter is a first-class provider offering unified access to 100+ models:

- OpenAI: GPT-4o, GPT-4o-mini, o1-preview
- Anthropic: Claude 3.5 Sonnet, Opus, Haiku
- Meta: Llama 3.1 405B, 70B, 8B
- Mistral: Large 2, Nemo, Codestral
- Google: Gemma 2, Gemini

**Benefits:**
- Single API key for all models
- Automatic failover/fallback
- Usage analytics across models
- Competitive pricing

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Deployment** | Library (`pip install retail-ontology`) + thin wrappers |
| **State** | Config-driven, adapters manage their own connections |
| **Scaling** | Library is stateless; adapters scale independently |
| **Latency** | In-process (library) + adapter overhead |
| **Development** | Library first, dogfood via thin wrappers |
| **Team** | Core team owns library; consumers own wrappers |
| **Extensibility** | Plugin system for adapters, LLM providers, metrics |

### Technology Stack

- **Core Library**: Pure Python, minimal deps (pydantic, pyyaml, networkx, instructor)
- **Adapters**: duckdb, psycopg2, snowflake-connector-python (optional deps)
- **LLM**: openai client (works for OpenRouter), ollama, llama-cpp-python
- **Distribution**: PyPI, uv, pipx for CLI tools
- **Testing**: pytest, hypothesis (property-based for query engine)

### Pros

- ✅ **True productization** - installable, versioned, reusable
- ✅ **Skill-ready** - natural fit for agent frameworks (LangChain, LlamaIndex, custom)
- ✅ **OpenRouter first-class** - 100+ models, single key, failover
- ✅ **Multi-database** - DuckDB for pilot, Postgres/Snowflake for prod
- ✅ **Thin wrappers** - CLI, Telegram, API, Web UI as separate packages
- ✅ **Embeddable** - use in notebooks, other apps, data pipelines
- ✅ **Clear boundaries** - ontology logic separated from interfaces
- ✅ **Monetizable** - core library can be commercial/enterprise

### Cons

- ❌ More upfront design work (stable APIs, versioning)
- ❌ Adapter pattern adds abstraction overhead
- ❌ Need to maintain multiple packages (or monorepo with publish pipeline)
- ❌ Library consumers may need migration guides
- ❌ Less control over deployment topology control (consumer decides)

### Best For

- **Long-term product vision** (skill, SaaS, embeddable library)
- **Multi-client deployments** (each client gets own adapter config)
- **OpenRouter-centric strategy** (model flexibility is key)
- **Team wants to dogfood library** via thin wrappers
- **Future: marketplace/skill distribution**
