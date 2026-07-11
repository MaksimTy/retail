"""
DuckDB Adapter for Retail Ontology Platform.

Implements the DataAdapter protocol for DuckDB database.
"""

import asyncio
from pathlib import Path
from typing import Any, Optional

import duckdb

from retail_ontology.adapters.base import DataAdapter, QueryResult, SchemaInfo


class DuckDBAdapter(DataAdapter):
    """DuckDB adapter implementation."""

    def __init__(self, database_path: str | Path, read_only: bool = False):
        """
        Initialize DuckDB adapter.

        Args:
            database_path: Path to DuckDB database file
            read_only: Whether to open in read-only mode
        """
        self.database_path = Path(database_path)
        self.read_only = read_only
        self._connection: Optional[duckdb.DuckDBPyConnection] = None

    async def connect(self) -> None:
        """Establish connection to DuckDB."""
        # Ensure parent directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Run in thread pool since duckdb is synchronous
        loop = asyncio.get_event_loop()
        self._connection = await loop.run_in_executor(
            None,
            lambda: duckdb.connect(str(self.database_path), read_only=self.read_only),
        )

    async def disconnect(self) -> None:
        """Close the connection to DuckDB."""
        if self._connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connection.close)
            self._connection = None

    async def execute(
        self, sql: str, params: Optional[dict[str, Any]] = None
    ) -> QueryResult:
        """
        Execute a SQL query and return results.

        Args:
            sql: SQL query to execute
            params: Optional parameters for parameterized query

        Returns:
            QueryResult with rows, columns, and row count
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")

        loop = asyncio.get_event_loop()

        def _execute() -> QueryResult:
            if params:
                result = self._connection.execute(sql, params)
            else:
                result = self._connection.execute(sql)

            rows = result.fetchall()
            columns = [desc[0] for desc in result.description] if result.description else []
            return QueryResult(rows=rows, columns=columns, row_count=len(rows))

        return await loop.run_in_executor(None, _execute)

    async def execute_many(self, sql: str, params_list: list[dict[str, Any]]) -> None:
        """
        Execute a SQL statement multiple times with different parameters.

        Args:
            sql: SQL statement to execute
            params_list: List of parameter dictionaries
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")

        loop = asyncio.get_event_loop()

        def _execute_many() -> None:
            for params in params_list:
                self._connection.execute(sql, params)

        await loop.run_in_executor(None, _execute_many)

    async def fetch_schema(self) -> SchemaInfo:
        """Fetch database schema information."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")

        loop = asyncio.get_event_loop()

        def _fetch_schema() -> SchemaInfo:
            # Get all tables
            tables_result = self._connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()

            tables = {}
            for (table_name,) in tables_result:
                # Get columns for each table
                columns_result = self._connection.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'main' AND table_name = ?
                    ORDER BY ordinal_position
                    """,
                    [table_name],
                ).fetchall()

                tables[table_name] = [
                    {
                        "name": col[0],
                        "type": col[1],
                        "nullable": col[2] == "YES",
                        "default": col[3],
                    }
                    for col in columns_result
                ]

            return SchemaInfo(tables=tables)

        return await loop.run_in_executor(None, _fetch_schema)

    async def health_check(self) -> bool:
        """Check if the connection is healthy."""
        try:
            if not self._connection:
                return False
            result = await self.execute("SELECT 1")
            return result.row_count == 1
        except Exception:
            return False

    async def __aenter__(self) -> "DuckDBAdapter":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get the underlying DuckDB connection (for advanced usage)."""
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._connection
