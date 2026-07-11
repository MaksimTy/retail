# Development Guide

## Retail Ontology Platform - Development Guide

This document provides comprehensive instructions for developing on the Retail Ontology Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Contributing](#contributing)

---

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Package Manager**: uv (recommended) or pip
- **Git**: For version control
- **Docker**: For containerized development (optional)

### Required Tools

```bash
# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pre-commit hooks
uv pip install pre-commit
pre-commit install
```

---

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/retail-ontology-platform.git
cd retail-ontology-platform
```

### 2. Install Dependencies

```bash
# Install all dependencies with extras
uv sync --all-extras

# Verify installation
uv pip list | grep retail
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 4. Download Sample Data

```bash
# Download UCI Online Retail dataset
make download

# Build DuckDB warehouse
make build-warehouse
```

### 5. Verify Setup

```bash
# Test CLI
retail ask "revenue by country"

# Test API
make run-api
# In another terminal:
curl http://localhost:8000/health
```

---

## Development Workflow

### Project Structure

```
retail-ontology-platform/
├── packages/
│   ├── retail-ontology/     # Core library
│   │   └── src/retail_ontology/
│   │       ├── concepts/     # Concept definitions
│   │       ├── metrics/      # Metric definitions
│   │       ├── relationships/ # Join path computation
│   │       ├── query_engine/  # NL→SQL translation
│   │       ├── adapters/     # Database adapters
│   │       ├── llm/          # LLM providers
│   │       └── scripts/      # Data pipeline
│   ├── retail-cli/          # CLI wrapper
│   ├── retail-telegram/     # Telegram bot
│   └── retail-api/          # REST API
├── docs/                    # Documentation
├── tests/                   # Integration tests
└── Makefile                 # Development commands
```

### Common Commands

```bash
# Install dependencies
make install

# Run all checks
make check

# Run tests
make test

# Run specific tests
uv run pytest packages/retail-ontology/tests -v

# Type checking
make typecheck

# Linting
make lint

# Formatting
make format

# Build packages
make build

# Clean build artifacts
make clean
```

### Development Commands

```bash
# Run CLI
uv run retail ask "revenue by country"

# Run API server
make run-api

# Run Telegram bot
make run-telegram

# Run with specific config
OPENROUTER_API_KEY=xxx uv run retail ask "revenue by country"
```

---

## Code Standards

### Python Version

- **Target**: Python 3.11+
- **Configuration**: `.python-version` file

### Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Format code
uv run ruff format .

# Check formatting
uv run ruff format --check .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

### Type Hints

All code must be fully typed. Use mypy for type checking.

```bash
# Type check
uv run mypy packages/retail-ontology/src

# Type check all packages
make typecheck
```

### Import Order

Ruff is configured to sort imports automatically:

```python
# Standard library
import json
import logging
from pathlib import Path
from typing import Optional

# Third-party
import duckdb
import pandas as pd
from pydantic import BaseModel

# Local imports
from retail_ontology.config import Settings
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_revenue(df: pd.DataFrame) -> float:
    """Calculate total revenue from DataFrame.

    Args:
        df: DataFrame with sales data.

    Returns:
        Total revenue as float.

    Raises:
        ValueError: If required columns are missing.
    """
    if "line_total" not in df.columns:
        raise ValueError("Missing 'line_total' column")
    return df["line_total"].sum()
```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
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
├── integration/             # Integration tests
│   ├── test_e2e_query.py
│   ├── test_adapter_swap.py
│   ├── test_cli.py
│   ├── test_telegram.py
│   └── test_api.py
└── fixtures/                # Test data
    └── sample_data.csv
```

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with coverage
make test-cov

# Run specific test file
uv run pytest packages/retail-ontology/tests/test_concepts.py -v

# Run specific test
uv run pytest packages/retail-ontology/tests/test_concepts.py::test_concept_registry -v
```

### Writing Tests

```python
import pytest
from retail_ontology.concepts import ConceptRegistry

def test_concept_registry_loads_from_yaml():
    """Test that registry loads concepts from YAML."""
    registry = ConceptRegistry.from_yaml("tests/fixtures/concepts.yaml")

    assert "customer" in registry.list()
    assert "product" in registry.list()

def test_concept_has_required_fields():
    """Test that concept has all required fields."""
    registry = ConceptRegistry.from_yaml("tests/fixtures/concepts.yaml")
    customer = registry.get("customer")

    assert customer.table == "dim_customer"
    assert customer.primary_key == "customer_key"
    assert len(customer.attributes) > 0
```

### Mocking LLM Calls

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_translator_with_mock_llm():
    """Test translator with mocked LLM response."""
    mock_response = {
        "metrics": ["total_revenue"],
        "dimensions": [{"concept": "customer", "attribute": "country"}],
        "filters": []
    }

    with patch("retail_ontology.llm.OpenRouterProvider") as mock_provider:
        mock_provider.return_value.complete_structured = AsyncMock(
            return_value=mock_response
        )

        # Test translator logic
        ...
```

---

## Debugging

### Enable Debug Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Mode

```python
import os
os.environ["LOG_LEVEL"] = "DEBUG"

from retail_ontology import OntologyEngine
engine = OntologyEngine.from_config("config.yaml")

# Ask with debug output
result = engine.ask("revenue by country")
```

### Interactive Debugging

```bash
# Start Python REPL with context
uv run python -i -c "
from retail_ontology import OntologyEngine
engine = OntologyEngine.from_config('config.yaml')
"

# Or use ipdb
uv run ipdb -c continue packages/retail-ontology/src/retail_ontology/query_engine/translator.py
```

### Debug Data Pipeline

```python
# Debug download script
uv run python -m retail_ontology.scripts.download_data --verbose

# Debug warehouse build
uv run python -m retail_ontology.scripts.build_warehouse --verbose
```

---

## Contributing

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/new-metric
   ```

2. **Make changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run checks**
   ```bash
   make check
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new metric for customer retention"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/new-metric
   ```

### Commit Message Format

Use conventional commits:

```
feat: add new metric for customer retention
fix: resolve issue with negative quantities
docs: update ontology guide
refactor: simplify adapter interface
test: add unit tests for translator
chore: update dependencies
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] PR description is clear

### Release Process

```bash
# Update version
bump2version patch

# Build packages
make build

# Publish to PyPI
make publish
```

---

## Development Environment

### Docker Development

```bash
# Build development image
docker build -t retail-ontology-dev -f Dockerfile.dev .

# Run with volume mount
docker run -v $(pwd):/app -w /app retail-ontology-dev bash

# Run tests in container
docker run -v $(pwd):/app -w /app retail-ontology-dev make test
```

### VS Code Configuration

Recommended extensions:
- Python
- Pylance
- Ruff
- Docker

VS Code settings (`.vscode/settings.json`):

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.analysis.typeCheckingMode": "strict"
}
```

---

## Architecture Decision Records (ADRs)

### Recording Decisions

When making significant architectural decisions, create an ADR:

```markdown
# ADR-001: Use OpenRouter as Primary LLM Provider

## Status

Accepted

## Context

We need to choose an LLM provider for the Retail Ontology Platform.

## Decision

Use OpenRouter as the primary provider with fallback to local models.

## Consequences

- Pros: Access to 100+ models, single API key, failover
- Cons: Dependency on external service, potential latency
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('engine.ask("revenue by country")', 'profile.out')

# Analyze results
stats = pstats.Stats('profile.out')
stats.sort_stats('cumulative').print_stats(10)
```

### Query Optimization

```python
# Enable query logging
from loguru import logger
logger.level("DEBUG")

# Check query execution time
import time
start = time.time()
result = engine.ask("revenue by country")
print(f"Execution time: {time.time() - start:.2f}s")
```

---

## Security

### Secrets Management

Never commit secrets to version control:

```bash
# Use .env file (gitignored)
echo "OPENROUTER_API_KEY=your-key" >> .env

# Or use environment variables
export OPENROUTER_API_KEY=your-key
```

### Dependency Scanning

```bash
# Check for vulnerabilities
uv pip install safety
safety check
```

---

## Support

For issues and questions:

1. Check existing [GitHub Issues](https://github.com/yourorg/retail-ontology-platform/issues)
2. Search documentation
3. Open a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
