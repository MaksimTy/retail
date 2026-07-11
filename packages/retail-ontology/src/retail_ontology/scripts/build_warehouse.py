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
from typing import Any

import duckdb
from loguru import logger
from pydantic import BaseModel, Field


class WarehouseConfig(BaseModel):
    """Configuration for warehouse building."""

    data_path: Path = Field(default=Path("./data/online_retail.csv"), description="Path to raw data CSV")
    duckdb_path: Path = Field(default=Path("./data/warehouse.duckdb"), description="Path to DuckDB database")
    batch_size: int = Field(default=10000, description="Batch size for data insertion")

    # Staging table name
    staging_table: str = Field(default="raw_transactions", description="Name of staging table")

    # Load order: dimensions first, then fact table
    load_order: list[str] = Field(
        default_factory=lambda: ["dim_customer", "dim_product", "dim_date", "fact_sales"],
        description="Order of table loading (dimensions before facts)",
    )

    # Table names for summary/validation
    dimension_tables: list[str] = Field(
        default_factory=lambda: ["dim_customer", "dim_product", "dim_date"],
        description="Dimension table names for summary",
    )
    fact_table: str = Field(default="fact_sales", description="Fact table name")

    # DDL statements for table creation
    ddl_statements: dict[str, str] = Field(
        default_factory=lambda: {
            "dim_customer": """
                CREATE TABLE IF NOT EXISTS dim_customer (
                    customer_key INTEGER PRIMARY KEY,
                    customer_id VARCHAR,
                    country VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "dim_product": """
                CREATE TABLE IF NOT EXISTS dim_product (
                    product_key INTEGER PRIMARY KEY,
                    stock_code VARCHAR,
                    description VARCHAR,
                    unit_price DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "dim_date": """
                CREATE TABLE IF NOT EXISTS dim_date (
                    date_key INTEGER PRIMARY KEY,
                    date VARCHAR,
                    year INTEGER,
                    quarter INTEGER,
                    month INTEGER,
                    day_of_month INTEGER,
                    day_of_week INTEGER,
                    is_weekend BOOLEAN
                );
            """,
            "fact_sales": """
                CREATE TABLE IF NOT EXISTS fact_sales (
                    sale_key INTEGER PRIMARY KEY,
                    invoice_no VARCHAR,
                    invoice_date VARCHAR,
                    quantity INTEGER,
                    unit_price DECIMAL(10, 2),
                    line_total DECIMAL(12, 2),
                    customer_key INTEGER,
                    product_key INTEGER,
                    date_key INTEGER,
                    is_return BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "indexes": """
                CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_key ON fact_sales(customer_key);
                CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key ON fact_sales(product_key);
                CREATE INDEX IF NOT EXISTS idx_fact_sales_invoice_date ON fact_sales(invoice_date);
                CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key ON fact_sales(date_key);
            """,
        },
        description="DDL statements for table creation",
    )

    # SQL statements for data loading (INSERT ... SELECT)
    load_statements: dict[str, str] = Field(
        default_factory=lambda: {
            "dim_customer": """
                INSERT INTO dim_customer (customer_key, customer_id, country)
                SELECT
                    ROW_NUMBER() OVER (ORDER BY customer_id) as customer_key,
                    customer_id,
                    country
                FROM (
                    SELECT
                        CAST("CustomerID" AS VARCHAR) as customer_id,
                        TRIM("Country") as country
                    FROM raw_transactions
                    WHERE "CustomerID" IS NOT NULL
                    GROUP BY CAST("CustomerID" AS VARCHAR), TRIM("Country")
                );
            """,
            "dim_product": """
                INSERT INTO dim_product (product_key, stock_code, description, unit_price)
                SELECT
                    ROW_NUMBER() OVER (ORDER BY stock_code) as product_key,
                    stock_code,
                    description,
                    unit_price
                FROM (
                    SELECT DISTINCT
                        "StockCode" as stock_code,
                        "Description" as description,
                        CAST("UnitPrice" AS DECIMAL(10, 2)) as unit_price
                    FROM raw_transactions
                    WHERE "Description" IS NOT NULL
                );
            """,
            "dim_date": """
                INSERT INTO dim_date (date_key, date, year, quarter, month, day_of_month, day_of_week, is_weekend)
                SELECT
                    CAST(REPLACE(CAST(date_str AS VARCHAR), '-', '') AS INTEGER) as date_key,
                    CAST(date_str AS VARCHAR) as date,
                    CAST(SUBSTR(CAST(date_str AS VARCHAR), 1, 4) AS INTEGER) as year,
                    CAST((CAST(SUBSTR(CAST(date_str AS VARCHAR), 6, 2) AS INTEGER) - 1) / 3 + 1 AS INTEGER) as quarter,
                    CAST(SUBSTR(CAST(date_str AS VARCHAR), 6, 2) AS INTEGER) as month,
                    CAST(SUBSTR(CAST(date_str AS VARCHAR), 9, 2) AS INTEGER) as day_of_month,
                    CAST((CAST(date_str AS DATE) - DATE '1970-01-01') % 7 + 1 AS INTEGER) as day_of_week,
                    CASE WHEN CAST((CAST(date_str AS DATE) - DATE '1970-01-01') % 7 + 1 AS INTEGER) IN (6, 7) THEN TRUE ELSE FALSE END as is_weekend
                FROM (
                    SELECT DISTINCT
                        CAST(strptime("InvoiceDate", '%m/%d/%Y %H:%M') AS DATE) as date_str
                    FROM raw_transactions
                    WHERE "InvoiceDate" IS NOT NULL
                );
            """,
            "fact_sales": """
                INSERT INTO fact_sales (sale_key, invoice_no, invoice_date, quantity, unit_price, line_total, customer_key, product_key, date_key, is_return)
                SELECT
                    ROW_NUMBER() OVER (ORDER BY t."InvoiceNo", t."StockCode") as sale_key,
                    t."InvoiceNo" as invoice_no,
                    CAST(t."InvoiceDate" AS VARCHAR) as invoice_date,
                    CAST(t."Quantity" AS INTEGER) as quantity,
                    CAST(t."UnitPrice" AS DECIMAL(10, 2)) as unit_price,
                    CAST(t."Quantity" * t."UnitPrice" AS DECIMAL(12, 2)) as line_total,
                    c.customer_key,
                    p.product_key,
                    CAST(REPLACE(CAST(DATE(strptime(t."InvoiceDate", '%m/%d/%Y %H:%M')) AS VARCHAR), '-', '') AS INTEGER) as date_key,
                    CASE WHEN CAST(t."Quantity" AS INTEGER) < 0 THEN TRUE ELSE FALSE END as is_return
                FROM raw_transactions t
                JOIN dim_customer c ON CAST(t."CustomerID" AS VARCHAR) = c.customer_id
                JOIN dim_product p ON t."StockCode" = p.stock_code
                WHERE t."CustomerID" IS NOT NULL
                  AND t."Description" IS NOT NULL
                  AND t."InvoiceNo" IS NOT NULL;
            """,
        },
        description="SQL statements for loading data into dimension and fact tables",
    )

    # Validation queries
    validation_queries: dict[str, str] = Field(
        default_factory=lambda: {
            "dim_customer_count": "SELECT COUNT(*) as count FROM dim_customer;",
            "dim_product_count": "SELECT COUNT(*) as count FROM dim_product;",
            "dim_date_count": "SELECT COUNT(*) as count FROM dim_date;",
            "fact_sales_count": "SELECT COUNT(*) as count FROM fact_sales;",
            "fact_sales_null_keys": "SELECT COUNT(*) as null_count FROM fact_sales WHERE customer_key IS NULL OR product_key IS NULL OR date_key IS NULL;",
            "fact_sales_returns": "SELECT COUNT(*) as return_count FROM fact_sales WHERE is_return = TRUE;",
            "fact_sales_negative_qty": "SELECT COUNT(*) as neg_count FROM fact_sales WHERE quantity < 0;",
        },
        description="Validation queries for data quality checks",
    )

    # Staging table cleaning rules
    cleaning_rules: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"column": "CustomerID", "description": "null CustomerID"},
            {"column": "Description", "description": "null Description"},
            {"column": "InvoiceNo", "description": "null InvoiceNo"},
        ],
        description="Rules for cleaning staging table (columns to check for NULL)",
    )

    # Summary display configuration
    summary_fields: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {"key": "dim_customer_count", "label": "Customers"},
            {"key": "dim_product_count", "label": "Products"},
            {"key": "dim_date_count", "label": "Dates"},
            {"key": "fact_sales_count", "label": "Sales"},
        ],
        description="Fields to display in summary with labels",
    )
    summary_extra_fields: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {"key": "fact_sales_returns", "label": "Returns"},
            {"key": "fact_sales_null_keys", "label": "Null FKs"},
        ],
        description="Extra fields to display in summary",
    )


class WarehouseEngine:
    """Engine for executing warehouse operations using WarehouseConfig."""

    def __init__(self, config: WarehouseConfig):
        """Initialize engine with configuration."""
        self.config = config

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Create and return a DuckDB connection."""
        self.config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(self.config.duckdb_path))

    def create_tables(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Create all tables using DDL statements from config."""
        logger.info("Creating tables...")
        for table_name, ddl in self.config.ddl_statements.items():
            logger.debug(f"Creating table: {table_name}")
            conn.execute(ddl)
        logger.info("All tables created successfully")

    def load_raw_data(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Load raw CSV data into staging table using DuckDB's CSV reader."""
        logger.info(f"Loading raw data from {self.config.data_path}")

        if not self.config.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.config.data_path}")

        conn.execute(f"""
            CREATE OR REPLACE TABLE {self.config.staging_table} AS
            SELECT * FROM read_csv_auto('{self.config.data_path}', HEADER=TRUE, SAMPLE_SIZE=-1)
        """)

        count = conn.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}").fetchone()[0]
        logger.info(f"Loaded {count} rows from raw data into staging table")

    def clean_staging_data(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Clean the staging data using SQL rules from config."""
        logger.info("Cleaning staging data...")

        initial_count = conn.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}").fetchone()[0]
        current_count = initial_count

        # Apply cleaning rules from config
        for rule in self.config.cleaning_rules:
            column = rule["column"]
            description = rule["description"]
            conn.execute(f'DELETE FROM {self.config.staging_table} WHERE "{column}" IS NULL')
            new_count = conn.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}").fetchone()[0]
            removed = current_count - new_count
            logger.info(f"Removed {removed} rows with {description}")
            current_count = new_count

        # Remove duplicates
        conn.execute(f"""
            CREATE OR REPLACE TABLE {self.config.staging_table} AS
            SELECT DISTINCT * FROM {self.config.staging_table}
        """)
        after_dedup = conn.execute(f"SELECT COUNT(*) FROM {self.config.staging_table}").fetchone()[0]
        logger.info(f"Removed {current_count - after_dedup} duplicate rows")

        logger.info(f"Data cleaning complete. Final row count: {after_dedup}")

    def load_dimensions_and_facts(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Load dimension and fact tables using configured SQL statements."""
        logger.info("Loading dimension and fact tables...")

        for table_name in self.config.load_order:
            if table_name in self.config.load_statements:
                logger.info(f"Loading {table_name}...")
                # Clear table before loading (idempotent)
                conn.execute(f"DELETE FROM {table_name}")
                conn.execute(self.config.load_statements[table_name])
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                logger.info(f"Loaded {count} rows into {table_name}")

        logger.info("All dimension and fact tables loaded successfully")

    def validate_warehouse(self, conn: duckdb.DuckDBPyConnection) -> dict[str, Any]:
        """Run validation queries from config and return results."""
        logger.info("Running warehouse validation...")

        results = {}
        for check_name, query in self.config.validation_queries.items():
            result = conn.execute(query).fetchone()
            results[check_name] = result[0] if result else 0
            logger.info(f"Validation [{check_name}]: {results[check_name]}")

        # Check for data quality issues
        if results.get("fact_sales_null_keys", 0) > 0:
            logger.warning(f"Found {results['fact_sales_null_keys']} rows with NULL foreign keys in fact_sales")

        if results.get("fact_sales_returns", 0) > 0:
            logger.info(f"Found {results['fact_sales_returns']} return transactions")

        logger.info("Warehouse validation complete")
        return results

    def print_summary(self, conn: duckdb.DuckDBPyConnection, validation_results: dict[str, Any]) -> None:
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

    def build(self) -> None:
        """Execute the full warehouse build pipeline."""
        conn = None
        try:
            conn = self.get_connection()
            self.create_tables(conn)
            self.load_raw_data(conn)
            self.clean_staging_data(conn)
            self.load_dimensions_and_facts(conn)
            validation_results = self.validate_warehouse(conn)
            self.print_summary(conn, validation_results)
            logger.info(f"Warehouse built successfully at {self.config.duckdb_path}")
        except Exception as e:
            logger.error(f"Failed to build warehouse: {e}")
            sys.exit(1)
        finally:
            if conn:
                conn.close()


def main() -> None:
    """Main entry point for warehouse building."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

    config = WarehouseConfig()
    engine = WarehouseEngine(config)
    engine.build()


if __name__ == "__main__":
    main()
