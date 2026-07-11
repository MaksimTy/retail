"""
Adapters package for Retail Ontology Platform.

Provides database adapter implementations for different backends.
"""

from retail_ontology.adapters.base import DataAdapter, QueryResult, SchemaInfo
from retail_ontology.adapters.duckdb import DuckDBAdapter

__all__ = [
    "DataAdapter",
    "QueryResult",
    "SchemaInfo",
    "DuckDBAdapter",
]
