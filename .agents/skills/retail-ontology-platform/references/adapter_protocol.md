# Adapter Protocol Reference

This document defines the `DataAdapter` protocol that all database adapters must implement.

## Protocol Definition

```python
from typing import Protocol, Optional, Any
from dataclasses import dataclass
from contextlib import AbstractAsyncContextManager

@dataclass
class QueryResult:
    """Result of a query execution."""
    rows: list[dict[str, Any]]
    columns: list[str]
    row_count: int
    execution_time_ms: float

@dataclass
class SchemaInfo:
    """Database schema information."""
    tables: dict[str, "TableInfo"]
    relationships: list["RelationshipInfo"]

@dataclass
class TableInfo:
    """Table metadata."""
    name: str
    columns: dict[str, "ColumnInfo"]
    primary_key: list[str]
    foreign_keys: list["ForeignKeyInfo"]
    row_count: Optional[int] = None

@dataclass
class ColumnInfo:
    """Column metadata."""
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False

@dataclass
class ForeignKeyInfo:
    """Foreign key metadata."""
    column: str
    referenced_table: str
    referenced_column: str

@dataclass
class RelationshipInfo:
    """Relationship between tables."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str  # "one-to-one", "one-to-many", "many-to-many"

class DataAdapter(Protocol):
    """Protocol for database adapters."""

    async def connect(self) -> None:
        """Establish connection to the database."""
        ...

    async def disconnect(self) -> None:
        """Close database connection."""
        ...

    async def execute(
        self,
        sql: str,
        params: Optional[dict[str, Any]] = None
    ) -> QueryResult:
        """Execute a single query and return results."""
        ...

    async def execute_many(
        self,
        sql: str,
        params_list: list[dict[str, Any]]
    ) -> None:
        """Execute a query multiple times with different parameters (batch)."""
        ...

    async def fetch_schema(self) -> SchemaInfo:
        """Fetch complete database schema information."""
        ...

    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        ...

    async def __aenter__(self) -> "DataAdapter":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
```

## Required Implementations

### DuckDB Adapter (`adapters/duckdb.py`)
- Connection pooling with `duckdb.connect()`
- Schema introspection via `PRAGMA` statements
- Parameterized queries with `?` placeholders
- Support for DuckDB-specific features (Parquet, JSON)

### PostgreSQL Adapter (`adapters/postgres.py`)
- Async connection pool with `asyncpg`
- SSL/TLS support
- Read replica support
- Alembic migration integration

### Snowflake Adapter (`adapters/snowflake.py`) - Optional
- `snowflake-connector-python` async support
- Snowflake-specific data types
- Stage/file format handling

## Usage Pattern

```python
from retail_ontology.adapters import DuckDBAdapter, PostgresAdapter
from retail_ontology.config import settings

# DuckDB (development)
async with DuckDBAdapter(settings.duckdb_path) as adapter:
    result = await adapter.execute("SELECT * FROM fact_sales LIMIT 10")
    schema = await adapter.fetch_schema()

# PostgreSQL (production)
async with PostgresAdapter(settings.postgres_dsn) as adapter:
    result = await adapter.execute("SELECT * FROM fact_sales LIMIT 10")
    schema = await adapter.fetch_schema()
```

## Error Handling

All adapters should raise consistent exceptions:

```python
class AdapterError(Exception):
    """Base adapter exception."""
    pass

class ConnectionError(AdapterError):
    """Connection failed."""
    pass

class QueryError(AdapterError):
    """Query execution failed."""
    def __init__(self, message: str, sql: str, params: Optional[dict] = None):
        self.sql = sql
        self.params = params
        super().__init__(message)

class SchemaError(AdapterError):
    """Schema operation failed."""
    pass
```

## Testing Requirements

Each adapter implementation must pass:
1. Connection lifecycle (connect/disconnect/context manager)
2. Basic query execution (SELECT, INSERT, UPDATE, DELETE)
3. Parameterized queries (SQL injection prevention)
4. Batch execution (`execute_many`)
5. Schema introspection accuracy
6. Health check reliability
7. Error handling for invalid SQL, connection loss, timeouts
8. Concurrent access (connection pool behavior)
