# Configuration Schema Reference

This document defines the complete Pydantic Settings configuration for the Retail Ontology Platform.

## Settings Class

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn
from typing import Literal, Optional
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "retail-ontology"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Data Layer
    duckdb_path: Path = Path("./data/warehouse.duckdb")
    postgres_dsn: Optional[PostgresDsn] = None
    warehouse_schema: str = "retail"

    # LLM Providers (OpenRouter is first-class)
    openrouter_api_key: str = Field(..., description="OpenRouter API key (required)")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_default_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_fallback_models: list[str] = [
        "openai/gpt-4o-mini",
        "google/gemini-1.5-flash",
        "meta-llama/llama-3.1-70b-instruct"
    ]

    # Fallback providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    llama_cpp_model_path: Optional[Path] = None

    # LLM Settings
    default_temperature: float = 0.1
    max_tokens: int = 4096
    request_timeout: float = 60.0
    max_retries: int = 3

    # Query Engine
    lqp_max_joins: int = 5
    lqp_max_filters: int = 10
    sql_timeout: float = 30.0
    max_rows_returned: int = 10000

    # CLI
    cli_output_format: Literal["table", "json", "csv", "markdown"] = "table"
    cli_show_sql: bool = False
    cli_stream: bool = True

    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_allowed_users: list[int] = Field(default_factory=list)
    telegram_session_timeout: int = 3600

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    api_rate_limit: int = 100
    api_rate_limit_window: int = 60
    api_auth_enabled: bool = False
    api_auth_secret: Optional[str] = None

    # Observability
    log_format: Literal["json", "console"] = "console"
    metrics_enabled: bool = True
    metrics_port: int = 9090
    tracing_enabled: bool = False
    tracing_endpoint: Optional[str] = None
    tracing_sample_rate: float = 0.1

    # Data Pipeline
    data_dir: Path = Path("./data")
    uci_dataset_url: str = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    warehouse_batch_size: int = 10000

    # Development
    dev_reload: bool = True
    dev_seed_data: bool = False
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `OPENROUTER_DEFAULT_MODEL` | No | `anthropic/claude-3.5-sonnet` | Default model |
| `DUCKDB_PATH` | No | `./data/warehouse.duckdb` | DuckDB file path |
| `POSTGRES_DSN` | No | - | PostgreSQL connection string |
| `TELEGRAM_BOT_TOKEN` | No | - | Telegram bot token |
| `API_AUTH_SECRET` | No | - | API auth secret (enables auth) |
| `LOG_LEVEL` | No | `INFO` | Log level |
| `ENVIRONMENT` | No | `development` | Environment name |

## Usage

```python
from retail_ontology.config import settings

# Access settings
db_path = settings.duckdb_path
api_key = settings.openrouter_api_key
model = settings.openrouter_default_model
