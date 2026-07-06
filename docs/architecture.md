# Retail AI Agent Architecture

## Overview

This project implements an AI agent that answers customer questions by directly querying modeled DWH objects (orders, contracts, customers, sales) rather than using traditional RAG with semantic search. This follows the **Ontology-Augmented Generation (OAG)** architecture pattern.

## Architecture Layers

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

## Key Components

### 1. Data Layer (Kimball Dimensional Model)
- **Source**: UCI Online Retail dataset (ID: 352)
- **Warehouse**: DuckDB with dimensional model
  - `dim_customer`: Customer dimension
  - `dim_product`: Product dimension
  - `fact_sales`: Sales fact table

### 2. Ontology Layer
- **Concepts**: Customer, Product, Order definitions
- **Metrics**: Total Revenue, AOV, Repeat Rate
- **Relationships**: Entity relationship graph
- **Query Builder**: NL → SQL translation

### 3. Agent Core
- **LLM Provider**: Ollama, OpenAI, Anthropic (pluggable)
- **Translator**: Converts natural language to SQL
- **Validator**: Ensures SQL safety

### 4. Interfaces
- **CLI**: Typer-based command-line interface
- **Telegram**: Future bot interface
- **REST API**: Future HTTP API

## Usage

### Setup
```bash
# Install dependencies
uv pip install -e .

# Download and process data
python scripts/download_data.py
python scripts/build_warehouse.py

# Or use the CLI
retail setup
```

### Ask a Question
```bash
# Via CLI
retail ask "What is the total revenue?"

# Interactive chat
retail chat
```

## Monetization Strategy

1. **Subscription Model**: Charge clients for access to the AI agent
2. **Custom Ontology Development**: Charge for building domain-specific ontologies
3. **Data Pipeline as a Service**: Offer ETL pipeline setup and maintenance
4. **Consulting**: Provide Kimball modeling and OAG architecture consulting