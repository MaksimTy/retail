"""
Base Adapter Protocol for Retail Ontology Platform.

Defines the interface that all data adapters must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional


@dataclass
class QueryResult:
    """Result of a query execution."""

    rows: list[tuple]
    columns: list[str]
    row_count: int


@dataclass
class SchemaInfo:
    """Database schema information."""

    tables: dict[str, list[dict[str, Any]]]


class DataAdapter(ABC):
    """Abstract base class for data adapters."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the data source."""
        ...

    @abstractmethod
    async def execute(self, sql: str, params: Optional[dict[str, Any]] = None) -> QueryResult:
        """Execute a SQL query and return results."""
        ...

    @abstractmethod
    async def execute_many(self, sql: str, params_list: list[dict[str, Any]]) -> None:
        """Execute a SQL statement multiple times with different parameters."""
        ...

    @abstractmethod
    async def fetch_schema(self) -> SchemaInfo:
        """Fetch database schema information."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the connection is healthy."""
        ...

    @abstractmethod
    async def __aenter__(self) -> "DataAdapter":
        """Async context manager entry."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        ...
