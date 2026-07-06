# Retail AI Agent with Ontology-Augmented Generation (OAG)

## Overview

This project implements an AI agent that answers customer questions by directly querying modeled DWH objects (orders, contracts, customers, sales) rather than using traditional RAG with semantic search. This follows the **Ontology-Augmented Generation (OAG)** architecture pattern used in Palantir Foundry and validated by Microsoft Research.

**Key Differentiator**: Deterministic, exact answers based on data structure — not probabilistic text that can hallucinate numbers.

## Architecture

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

## Features

- **Deterministic Answers**: Get exact answers from your data, not hallucinated text
- **Multi-Provider LLM Support**: Ollama (local), OpenAI, Anthropic
- **Kimball Dimensional Model**: Properly modeled data warehouse
- **Extensible Ontology**: Add new concepts and metrics easily
- **Multiple Interfaces**: CLI, Telegram Bot, REST API

## Data Source

This project uses the [UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) (ID: 352).

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd retail

# Install dependencies
uv pip install -e .

# Setup the data warehouse
retail setup
```

## Usage

### CLI Interface

```bash
# Ask a question
retail ask "What is the total revenue?"

# Interactive chat
retail chat

# Show configuration info
retail info
```

### REST API

```bash
# Start the API server
uvicorn src.retail.interfaces.api.routes:app --reload

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total revenue?"}'
```

### Telegram Bot

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your-bot-token"

# Run the bot
python -m src.retail.interfaces.telegram.bot
```

## Configuration

Create a `.env` file in the project root:

```env
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# OpenAI (optional)
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your-bot-token

# Database
DUCKDB_DATABASE_PATH=./data/warehouse/retail.duckdb
```

## Project Structure

```
retail/
├── src/retail/
│   ├── config/           # Configuration settings
│   ├── data/             # Data layer (Kimball model)
│   │   ├── source/       # Data source (UCI downloader)
│   │   ├── staging/      # Data cleaning
│   │   ├── warehouse/    # Dimensional model
│   │   └── access/       # Data access layer
│   ├── ontology/         # Ontology layer
│   │   ├── concepts/     # Business concept definitions
│   │   ├── metrics/      # Metric definitions
│   │   ├── relationships/# Entity relationships
│   │   └── query_builder/# NL to SQL translation
│   ├── agent/            # Agent core
│   │   ├── llm/          # LLM providers
│   │   ├── core.py       # Agent orchestration
│   │   └── tools.py      # Function calling tools
│   ├── interfaces/       # User interfaces
│   │   ├── cli/          # Command-line interface
│   │   ├── telegram/     # Telegram bot
│   │   └── api/          # REST API
│   └── deployment/         # Deployment scripts
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## Monetization Strategy

1. **Subscription Model**: Charge clients for access to the AI agent
2. **Custom Ontology Development**: Charge for building domain-specific ontologies
3. **Data Pipeline as a Service**: Offer ETL pipeline setup and maintenance
4. **Consulting**: Provide Kimball modeling and OAG architecture consulting

## License

MIT License
