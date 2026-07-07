# retail-api

REST API wrapper for the Retail Ontology Platform.

## Features

- **POST /ask** - Natural language queries (sync)
- **POST /ask/stream** - Streaming responses (Server-Sent Events)
- **GET /health** - Health check endpoint
- **GET /concepts** - List all concepts
- **GET /metrics** - List all metrics
- **GET /schema** - Database schema introspection
- **Authentication** - API key based auth
- **Rate limiting** - Per-client rate limits

## Installation

```bash
# From monorepo root
uv sync --all-extras

# Or install directly
pip install retail-api
```

## Configuration

Set environment variables:

```bash
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_KEY=your_api_key  # Optional, for authentication
```

## Usage

```bash
# Development
uv run uvicorn retail_api.main:app --host 0.0.0.0 --port 8000 --reload

# Production
uv run uvicorn retail_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Ask a Question (Sync)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"question": "revenue by country", "session_id": "optional"}'
```

### Ask a Question (Stream)
```bash
curl -X POST http://localhost:8000/ask/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"question": "revenue by country"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### List Concepts
```bash
curl http://localhost:8000/concepts
```

### List Metrics
```bash
curl http://localhost:8000/metrics
```

### Database Schema
```bash
curl http://localhost:8000/schema
```

## Development

```bash
# Run tests
uv run pytest packages/retail-api/tests -v

# Type check
uv run mypy packages/retail-api/src

# Build
cd packages/retail-api && uv build
```

## Package Structure

```
retail-api/
├── pyproject.toml
├── README.md
├── src/
│   └── retail_api/
│       ├── __init__.py
│       ├── main.py              # FastAPI app entry point
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── ask.py           # /ask, /ask/stream endpoints
│       │   ├── health.py        # /health endpoint
│       │   ├── concepts.py      # /concepts endpoint
│       │   ├── metrics.py       # /metrics endpoint
│       │   └── schema.py        # /schema endpoint
│       ├── models/
│       │   ├── __init__.py
│       │   ├── request.py       # Request models
│       │   └── response.py      # Response models
│       ├── auth.py              # Authentication
│       ├── rate_limit.py        # Rate limiting
│       └── middleware.py        # Logging, error handling
└── tests/
    ├── test_ask.py
    ├── test_health.py
    ├── test_concepts.py
    ├── test_metrics.py
    └── test_auth.py