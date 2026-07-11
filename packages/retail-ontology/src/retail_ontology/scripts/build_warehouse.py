"""
DuckDB Warehouse Builder.

ETL pipeline that transforms raw UCI Online Retail data into a dimensional model
in DuckDB. Implements Kimball dimensional modeling with surrogate keys.

Usage:
    python -m retail_ontology.scripts.build_warehouse
    retail-build
"""

import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from retail_ontology.adapters.duckdb import DuckDBAdapter
from retail_ontology.scripts.schema import (
    ALL_TABLES,
    CLEANING_RULES,
    DIMENSION_TABLES,
    FACT_TABLE,
    LOAD_ORDER,
    SOURCE_COLUMNS,
    STAGING_TABLE,
    VALIDATION_QUERIES,
    generate_ddl,
    generate_indexes,
    get_all_ddl,
    get_load_statements,
    SUMMARY_EXTRA_FIELDS,
    SUMMARY_FIELDS,
)


class WarehouseConfig:
    """Configuration for warehouse building."""

    def __init__(
        self,
        data_path: Path = Path("./data/online_retail.csv"),
        duckdb_path: Path = Path("./data/warehouse.duckdb"),
        batch_size: int = 10000,
        csv_sample_size: int = -1,
    ):
        """
        Initialize warehouse configuration.

        Args:
            data_path: Path to raw data CSV
            duckdb_path: Path to DuckDB database
            batch_size: Batch size for data insertion
            csv_sample_size: Sample size for CSV reader (-1 for full scan)
        """
        self.data_path = data_path
        self.duckdb_path = duckdb_path
        self.batch_size = batch_size
        self.csv_sample_size = csv_sample_size

        # Table names
        self.staging_table = STAGING_TABLE
        self.load_order = LOAD_ORDER
        self.dimension_tables = DIMENSION_TABLES
        self.fact_table = FACT_TABLE

        # Schema and SQL
        self.ddl_statements = get_all_ddl()
        self.load_statements = get_load_statements()
        self.validation_queries = VALIDATION_QUERIES
        self.cleaning_rules = CLEANING_RULES
        self.summary_fields = SUMMARY_FIELDS
        self.summary_extra_fields = SUMMARY_EXTRA_FIELDS


class WarehouseEngine:
    """Engine for executing warehouse operations using WarehouseConfig."""

    def __init__(self, config: WarehouseConfig):
        """Initialize engine with configuration."""
        self.config = config
        self._adapter: DuckDBAdapter | None = None

    async def get_adapter(self) -> DuckDBAdapter:
        """Get or create DuckDB adapter."""
        if self._adapter is None:
            self._adapter = DuckDBAdapter(self.config.duckdb_path)
            await self._adapter.connect()
        return self._adapter

    async def create_tables(self) -> None:
        """Create all tables using DDL statements from schema."""
        adapter = await self.get_adapter()
        logger.info("Creating tables...")

        for table in ALL_TABLES:
            logger.debug(f"Creating table: {table.name}")
            ddl = generate_ddl(table)
            await adapter.execute(ddl)

            # Create indexes
            for idx_sql in generate_indexes(table):
                await adapter.execute(idx_sql)

        logger.info("All tables created successfully")

    async def load_raw_data(self) -> None:
        """Load raw CSV data into staging table using DuckDB's CSV reader."""
        adapter = await self.get_adapter()
        logger.info(f"Loading raw data from {self.config.data_path}")

        if not self.config.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.config.data_path}")

        # Use parameterized query to avoid SQL injection
        csv_path = str(self.config.data_path)
        await adapter.execute(
            f"""
            CREATE OR REPLACE TABLE {self.config.staging_table} AS
            SELECT * FROM read_csv_auto(?, HEADER=TRUE, SAMPLE_SIZE=?)
            """,
            [csv_path, self.config.csv_sample_size],
        )

        count_result = await adapter.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}")
        count = count_result.rows[0][0] if count_result.rows else 0
        logger.info(f"Loaded {count} rows from raw data into staging table")

    async def clean_staging_data(self) -> None:
        """Clean the staging data using SQL rules from schema."""
        adapter = await self.get_adapter()
        logger.info("Cleaning staging data...")

        initial_count_result = await adapter.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}")
        initial_count = initial_count_result.rows[0][0] if initial_count_result.rows else 0
        current_count = initial_count

        # Apply cleaning rules from schema
        for rule in self.config.cleaning_rules:
            column = rule["column"]
            description = rule["description"]
            await adapter.execute(f'DELETE FROM {self.config.staging_table} WHERE "{column}" IS NULL')
            new_count_result = await adapter.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}")
            new_count = new_count_result.rows[0][0] if new_count_result.rows else 0
            removed = current_count - new_count
            logger.info(f"Removed {removed} rows with {description}")
            current_count = new_count

        # Also remove empty strings for key columns
        for column in [SOURCE_COLUMNS["customer_id"], SOURCE_COLUMNS["description"], SOURCE_COLUMNS["invoice_no"]]:
            # Cast to VARCHAR first since some columns may be numeric
            await adapter.execute(f'DELETE FROM {self.config.staging_table} WHERE TRIM(CAST("{column}" AS VARCHAR)) = \'\'')
            new_count_result = await adapter.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}")
            new_count = new_count_result.rows[0][0] if new_count_result.rows else 0
            removed = current_count - new_count
            if removed > 0:
                logger.info(f"Removed {removed} rows with empty {column}")
            current_count = new_count

        # Remove duplicates based on business keys (not entire row)
        # Use business key columns to identify duplicates
        business_keys = [
            SOURCE_COLUMNS["invoice_no"],
            SOURCE_COLUMNS["stock_code"],
            SOURCE_COLUMNS["invoice_date"],
            SOURCE_COLUMNS["customer_id"],
        ]
        keys_str = ", ".join(f'"{k}"' for k in business_keys)
        await adapter.execute(f"""
            CREATE OR REPLACE TABLE {self.config.staging_table} AS
            SELECT DISTINCT ON ({keys_str}) *
            FROM {self.config.staging_table}
            ORDER BY {keys_str}
        """)

        after_dedup_result = await adapter.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}")
        after_dedup = after_dedup_result.rows[0][0] if after_dedup_result.rows else 0
        logger.info(f"Removed {current_count - after_dedup} duplicate rows")

        logger.info(f"Data cleaning complete. Final row count: {after_dedup}")

    async def load_dimensions_and_facts(self) -> None:
        """Load dimension and fact tables using configured SQL statements."""
        adapter = await self.get_adapter()
        logger.info("Loading dimension and fact tables...")

        for table_name in self.config.load_order:
            if table_name in self.config.load_statements:
                logger.info(f"Loading {table_name}...")
                # Clear table before loading (idempotent)
                await adapter.execute(f"DELETE FROM {table_name}")
                await adapter.execute(self.config.load_statements[table_name])
                count_result = await adapter.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = count_result.rows[0][0] if count_result.rows else 0
                logger.info(f"Loaded {count} rows into {table_name}")

        logger.info("All dimension and fact tables loaded successfully")

    async def validate_warehouse(self) -> dict[str, int]:
        """Run validation queries from schema and return results."""
        adapter = await self.get_adapter()
        logger.info("Running warehouse validation...")

        results = {}
        for check_name, query in self.config.validation_queries.items():
            result = await adapter.execute(query)
            results[check_name] = result.rows[0][0] if result.rows else 0
            logger.info(f"Validation [{check_name}]: {results[check_name]}")

        # Check for data quality issues
        if results.get("fact_sales_null_keys", 0) > 0:
            logger.warning(f"Found {results['fact_sales_null_keys']} rows with NULL foreign keys in fact_sales")

        if results.get("fact_sales_returns", 0) > 0:
            logger.info(f"Found {results['fact_sales_returns']} return transactions")

        logger.info("Warehouse validation complete")
        return results

    async def print_summary(self, validation_results: dict[str, int]) -> None:
        """Log warehouse summary using logger and config."""
        logger.info("=" * 60)
        logger.info("WAREHOUSE BUILD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Database: {self.config.duckdb_path}")
        logger.info(f"Built at: {datetime.now().isoformat()}")
        logger.info("-" * 60)

        # Main summary fields from config
        for field in self.config.summary_fields:
            key = field["key"]
            label = field["label"]
            value = validation_results.get(key, 0)
            logger.info(f"{label}: {value:,}")

        logger.info("-" * 60)

        # Extra summary fields from config
        for field in self.config.summary_extra_fields:
            key = field["key"]
            label = field["label"]
            value = validation_results.get(key, 0)
            logger.info(f"{label}: {value:,}")

        logger.info("=" * 60)

    async def build(self) -> None:
        """Execute the full warehouse build pipeline."""
        try:
            await self.create_tables()
            await self.load_raw_data()
            await self.clean_staging_data()
            await self.load_dimensions_and_facts()
            validation_results = await self.validate_warehouse()
            await self.print_summary(validation_results)
            logger.info(f"Warehouse built successfully at {self.config.duckdb_path}")
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            sys.exit(1)
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to build warehouse: {e}")
            sys.exit(1)
        finally:
            if self._adapter:
                await self._adapter.disconnect()


def main() -> None:
    """Main entry point for warehouse building."""
    import asyncio

    async def _run() -> None:
        logger.remove()
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

        config = WarehouseConfig()
        engine = WarehouseEngine(config)
        await engine.build()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
