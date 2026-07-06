# Retail AI Agent with Ontology-Augmented Generation (OAG)

## Executive Summary

This project implements an AI agent that answers customer questions by directly querying modeled DWH objects (orders, contracts, customers, sales) rather than using traditional RAG with semantic search. This follows the **Ontology-Augmented Generation (OAG)** architecture pattern used in Palantir Foundry and validated by Microsoft Research.

**Key Differentiator**: Deterministic, exact answers based on data structure — not probabilistic text that can hallucinate numbers.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RETAIL AI AGENT (OAG)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  INTERFACES  │───▶│  AGENT CORE  │───▶│  ONTOLOGY    │───▶│  DATA    │  │
│  │  (CLI, TG,   │    │  (Orchestr-  │    │  LAYER       │    │  LAYER   │  │
│  │   API, etc.) │    │   ation)     │    │  (Semantic   │    │  (DWH/   │  │
│  └──────────────┘    └──────────────┘    │   Mapping)   │    │   Kimball)│  │
│                                          └──────────────┘    └──────────┘  │
│                                                 │              │            │
│                                                 ▼              ▼            │
│                                          ┌──────────────┐    ┌──────────┐  │
│                                          │  LLM PROVIDER│    │  UCI     │  │
│                                          │  (Local/     │    │  ML REPO │  │
│                                          │   Cloud)     │    │  (Source)│  │
│                                          └──────────────┘    └──────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Data Layer (DWH / Kimball Modeling)

### Responsibility
- Extract, transform, load data from UCI ML Repository
- Build dimensional model (Kimball methodology)
- Provide typed, validated data access

### Components

| Component | Purpose |
|-----------|---------|
| `data/source/` | UCI ML Repository downloader using `ucimlrepo` |
| `data/staging/` | Raw data validation & cleaning |
| `data/warehouse/` | Dimensional model (facts + dimensions) |
| `data/access/` | Typed data access layer (SQLAlchemy/Polars) |

### Dimensional Model (Online Retail Dataset)

```
┌─────────────────┐     ┌─────────────────┐
│  dim_customer   │     │  dim_product    │
├─────────────────┤     ├─────────────────┤
│ customer_key (PK)│     │ product_key (PK)│
│ customer_id     │     │ stock_code      │
│ country         │     │ description     │
└────────┬────────┘     │ unit_price      │
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│           fact_sales                    │
├─────────────────────────────────────────┤
│ sale_key (PK)                           │
│ customer_key (FK)                       │
│ product_key (FK)                        │
│ invoice_no                              │
│ invoice_date                            │
│ quantity                                │
│ unit_price                              │
│ line_total (quantity * unit_price)      │
└─────────────────────────────────────────┘
```

### Technology Choices
- **DuckDB** — embedded analytical database, zero-config, perfect for pilot
- **Polars** — fast DataFrame operations for ETL
- **SQLAlchemy** — ORM for typed data access
- **ucimlrepo** — UCI dataset downloader

---

## Layer 2: Ontology / Semantic Layer (OAG Core)

### Responsibility
- Map natural language → structured queries against dimensional model
- Define business concepts, metrics, relationships
- Enable deterministic query generation

### Components

| Component | Purpose |
|-----------|---------|
| `ontology/concepts/` | Business concept definitions (Customer, Product, Order, Revenue) |
| `ontology/metrics/` | Metric definitions (Total Revenue, Avg Order Value, Repeat Rate) |
| `ontology/relationships/` | Entity relationships & join paths, hierarchies |
| `ontology/query_builder/` | NL → SQL/Query translation |

### Ontology Definition Example (YAML/JSON)

```yaml
concepts:
  customer:
    table: dim_customer
    primary_key: customer_key
    attributes:
      - name: customer_id
        type: string
      - name: country
        type: string
  
  product:
    table: dim_product
    primary_key: product_key
    attributes:
      - name: stock_code
        type: string
      - name: description
        type: string
      - name: unit_price
        type: decimal

metrics:
  total_revenue:
    expression: "SUM(fact_sales.line_total)"
    grain: [customer_key, product_key, invoice_date]
  
  avg_order_value:
    expression: "AVG(fact_sales.line_total)"
    grain: [invoice_no]

relationships:
  - from: fact_sales.customer_key
    to: dim_customer.customer_key
    type: many_to_one
  - from: fact_sales.product_key
    to: dim_product.product_key
    type: many_to_one
```

### Query Generation Flow

```
User Question: "What was total revenue from UK customers in December 2011?"
                    │
                    ▼
         ┌─────────────────────┐
         │  LLM + Ontology     │
         │  (Few-shot prompt)  │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Structured Query   │
         │  (SQL/IR)           │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Deterministic      │
         │  Execution          │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Exact Answer       │
         │  "£1,234,567.89"    │
         └─────────────────────┘
```

---

## Layer 3: AI Agent Layer (LLM Integration)

### Responsibility
- Orchestrate NL → Query → Answer pipeline
- Support multiple LLM providers (local + cloud)
- Handle conversation context, clarification

### LLM Provider Abstraction

```python
# Abstract interface
class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str: ...
    
    @abstractmethod
    async def complete_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel: ...

# Implementations
class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...
class OllamaProvider(LLMProvider): ...      # Local
class LlamaCppProvider(LLMProvider): ...    # Local
class VLLMProvider(LLMProvider): ...        # Local/Cloud
```

### Configuration (Environment-based)

```yaml
llm:
  provider: "ollama"  # openai, anthropic, ollama, llamacpp, vllm
  model: "llama3.1:8b"
  base_url: "http://localhost:11434"  # for local
  api_key: "${OPENAI_API_KEY}"        # for cloud
  temperature: 0.1
  max_tokens: 4096
```

---

## Layer 4: Interface Layer

### Phase 1: CLI (Current)
- Interactive REPL for questions
- Batch mode for testing
- Rich output formatting

### Phase 2: Telegram Bot
- `python-telegram-bot` v20+
- Command handlers (`/start`, `/help`, `/ask`)
- Inline queries support
- User session management

### Phase 3: REST API (Future)
- FastAPI service
- OpenAPI spec
- Authentication/rate limiting

### Phase 4: Web UI (Future)
- React/Streamlit frontend
- Conversation history
- Visualization of results

---

## Project Structure

```
retail/
├── pyproject.toml              # uv project config
├── uv.lock
├── README.md
├── ARCHITECTURE.md             # This file
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
│   │   └── test_interfaces/
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

---

## Dependencies (pyproject.toml)

### Core
- `python >= 3.11`
- `uv` — package manager

### Data Layer
- `duckdb >= 1.0` — embedded analytical DB
- `polars >= 1.0` — fast DataFrames
- `sqlalchemy >= 2.0` — ORM
- `ucimlrepo >= 0.0.7` — UCI dataset access

### Ontology Layer
- `pyyaml >= 6.0` — ontology definitions
- `networkx >= 3.0` — relationship graph

### Agent Layer
- `pydantic >= 2.0` — validation, settings
- `pydantic-settings >= 2.0` — config management
- `instructor >= 1.0` — structured LLM output
- `tenacity >= 8.0` — retries

### LLM Providers
- `openai >= 1.0` — OpenAI API
- `anthropic >= 0.30` — Anthropic API
- `ollama >= 0.3` — Ollama local
- `llama-cpp-python >= 0.2` — llama.cpp (optional)
- `vllm >= 0.5` — vLLM (optional)

### Interfaces
- `typer >= 0.9` — CLI framework
- `rich >= 13.0` — terminal formatting
- `python-telegram-bot >= 20.0` — Telegram bot
- `fastapi >= 0.109` — REST API (future)
- `uvicorn >= 0.27` — ASGI server (future)

### Development
- `pytest >= 7.0`
- `pytest-asyncio >= 0.23`
- `pytest-cov >= 4.0`
- `ruff >= 0.3` — linting
- `mypy >= 1.0` — type checking
- `pre-commit >= 3.0`

---

## Deployment Strategy

### Local Development
```bash
# Setup
uv sync
cp .env.example .env
# Edit .env with your LLM config

# Download & build data
uv run python -m retail.deployment.scripts.download_data
uv run python -m retail.deployment.scripts.build_warehouse

# Run CLI
uv run retail

# Run Telegram bot
uv run python -m retail.interfaces.telegram.bot
```

### Docker (Production)
```bash
docker-compose up -d
```

### Environment Variables
```env
# LLM Configuration
LLM_PROVIDER=ollama          # openai, anthropic, ollama, llamacpp, vllm
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=                 # for cloud providers
LLM_TEMPERATURE=0.1

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

---

## Development Phases

### Phase 1: Foundation (Week 1-2) ✓ Current
- [x] Project structure & config
- [ ] Data layer: UCI download → DuckDB warehouse
- [ ] Ontology: Concepts, metrics, relationships for Online Retail
- [ ] Agent core: NL → SQL translation with local LLM (Ollama)
- [ ] CLI interface with Rich formatting

### Phase 2: Telegram Bot (Week 3)
- [ ] Telegram bot with command handlers
- [ ] Session management
- [ ] Inline query support
- [ ] Deployment scripts

### Phase 3: Production Hardening (Week 4)
- [ ] Cloud LLM support (OpenAI, Anthropic)
- [ ] Query validation & safety
- [ ] Comprehensive tests
- [ ] Documentation
- [ ] Docker deployment

### Phase 4: Productization (Future)
- [ ] REST API
- [ ] Multi-tenant support
- [ ] Custom ontology builder
- [ ] Web UI
- [ ] Skill package for distribution

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **DuckDB** | Zero-config, embedded, analytical workloads, perfect for pilot |
| **Kimball Modeling** | Industry standard, aligns with existing practice, deterministic |
| **Ontology as YAML** | Human-readable, version-controlled, LLM-friendly |
| **Provider Abstraction** | Swap local/cloud without code changes |
| **Structured Output (Instructor)** | Guaranteed valid query generation |
| **uv** | Fast, modern Python packaging, lockfile |
| **Typer + Rich** | Best-in-class CLI experience |

---

## Success Metrics (Pilot)

| Metric | Target |
|--------|--------|
| Query accuracy (vs ground truth) | > 95% |
| Response latency (local LLM) | < 5s |
| Response latency (cloud LLM) | < 3s |
| Ontology coverage (business questions) | 80% of common retail questions |
| Setup time (fresh env) | < 5 min |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM generates invalid SQL | Structured output + validator + few-shot prompts |
| Local LLM quality insufficient | Start with cloud, optimize prompts, fallback to cloud |
| Ontology maintenance burden | YAML definitions + auto-generation from schema |
| Data freshness | Incremental ETL, scheduled refresh |
| Security (SQL injection) | Parameterized queries, no raw SQL execution |

---

## Next Steps

1. **Review this architecture** with stakeholders
2. **Create detailed implementation plan** (using `writing-plans` skill)
3. **Set up development environment** with uv
4. **Implement Phase 1** components in order:
   - Config & settings
   - Data layer (download → warehouse)
   - Ontology definitions
   - Agent core with Ollama
   - CLI interface
5. **Validate with real questions** from Online Retail dataset