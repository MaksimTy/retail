# retail

AI agent with Ontology-Augmented Generation (OAG) for retail analytics

## Project Goals

1. Build a headless ontology platform (Variant 3) as the primary architecture
2. Maintain alternative architecture variants in `plans/` directory
3. Enable reusable ontology library with multiple interface adapters
4. Support OpenRouter-first LLM integration
5. Provide scalable data layer options (DuckDB → Postgres/Snowflake)

## Architecture

**Selected: Variant 3 - Headless Ontology Platform (Library/Skill Architecture)**

See [`plans/VARIANT_3_HEADLESS_LIBRARY.md`](plans/VARIANT_3_HEADLESS_LIBRARY.md) for full architecture details, package structure, implementation plan, and API design.

### Core Components

- `retail-ontology` library (Python package) - Core ontology + query engine
- Thin interface adapters (CLI, Telegram, REST API)
- OpenRouter-first LLM provider abstraction (100+ models)
- Multi-database support (DuckDB, Postgres, Snowflake future)

### Key Features

- Reusable ontology definitions and metrics
- Natural language to SQL query translation via Logical Query Plans (LQP)
- Conversation context management
- Plugin architecture for adapters and LLM providers
- Production-ready library structure with PyPI distribution

## Architecture Variants

The following variants are documented in `plans/`:
- `plans/VARIANT_1_MONOLITHIC.md` - Monolithic embedded architecture
- `plans/VARIANT_2_SERVICE_ORIENTED.md` - Service-oriented architecture
- `plans/VARIANT_3_HEADLESS_LIBRARY.md` - Headless ontology platform (**SELECTED**)

## Getting Started

```bash
# Install dependencies (when implemented)
uv sync

# Download data
retail download

# Build warehouse
retail build

# Ask questions
retail ask "What was total revenue in Dec 2011?"
```

## Roadmap

1. Phase 1: Core library with DuckDB support
2. Phase 2: OpenRouter integration and Telegram/REST interfaces
3. Phase 3: Postgres adapter and production hardening
