# retail-telegram

Telegram bot wrapper for the Retail Ontology Platform.

## Features

- **/ask** - Natural language queries via LLM
- **Inline queries** - Quick metric lookups
- **Session management** - Per-user conversation context
- **Rich formatting** - Markdown responses with tables

## Installation

```bash
# From monorepo root
uv sync --all-extras

# Or install directly
pip install retail-telegram
```

## Configuration

Set environment variables:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook  # Optional, for webhook mode
```

## Usage

```bash
# Run in polling mode (development)
python -m retail_telegram.main

# Run with webhook (production)
uvicorn retail_telegram.webhook:app --host 0.0.0.0 --port 8000
```

## Development

```bash
# Run tests
uv run pytest packages/retail-telegram/tests -v

# Type check
uv run mypy packages/retail-telegram/src

# Build
cd packages/retail-telegram && uv build
```

## Package Structure

```
retail-telegram/
├── pyproject.toml
├── README.md
├── src/
│   └── retail_telegram/
│       ├── __init__.py
│       ├── main.py              # Polling mode entry point
│       ├── webhook.py           # Webhook mode (FastAPI)
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── ask.py           # /ask command handler
│       │   ├── inline.py        # Inline query handler
│       │   └── session.py       # Session management
│       ├── formatters.py        # Message formatting
│       └── middleware.py        # Logging, error handling
└── tests/
    ├── test_handlers.py
    └── test_formatters.py