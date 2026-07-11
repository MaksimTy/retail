"""
Schema definitions for Retail Ontology Warehouse.

Defines table schemas, DDL statements, and column mappings in a structured way.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Column:
    """Column definition for a table."""

    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    default: str | None = None
    description: str = ""


@dataclass(frozen=True)
class TableSchema:
    """Table schema definition."""

    name: str
    columns: list[Column]
    indexes: list[list[str]] | None = None
    description: str = ""


# Source column mappings (from raw CSV to staging)
SOURCE_COLUMNS = {
    "invoice_no": "InvoiceNo",
    "stock_code": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "invoice_date": "InvoiceDate",
    "unit_price": "UnitPrice",
    "customer_id": "CustomerID",
    "country": "Country",
}

# Table schemas
DIM_CUSTOMER = TableSchema(
    name="dim_customer",
    description="Customer dimension table with surrogate key",
    columns=[
        Column(name="customer_key", type="INTEGER", primary_key=True, nullable=False, description="Surrogate key"),
        Column(name="customer_id", type="VARCHAR", nullable=False, description="Original customer ID from source"),
        Column(name="country", type="VARCHAR", nullable=True, description="Customer country"),
        Column(name="created_at", type="TIMESTAMP", default="CURRENT_TIMESTAMP", description="Record creation timestamp"),
    ],
    indexes=[["customer_id"]],
)

DIM_PRODUCT = TableSchema(
    name="dim_product",
    description="Product dimension table with surrogate key",
    columns=[
        Column(name="product_key", type="INTEGER", primary_key=True, nullable=False, description="Surrogate key"),
        Column(name="stock_code", type="VARCHAR", nullable=False, description="Product stock code"),
        Column(name="description", type="VARCHAR", nullable=True, description="Product description"),
        Column(name="unit_price", type="DECIMAL(10, 2)", nullable=True, description="Product unit price"),
        Column(name="created_at", type="TIMESTAMP", default="CURRENT_TIMESTAMP", description="Record creation timestamp"),
    ],
    indexes=[["stock_code"]],
)

DIM_DATE = TableSchema(
    name="dim_date",
    description="Date dimension table with surrogate key",
    columns=[
        Column(name="date_key", type="INTEGER", primary_key=True, nullable=False, description="Surrogate key (YYYYMMDD)"),
        Column(name="date", type="VARCHAR", nullable=False, description="Date string (YYYY-MM-DD)"),
        Column(name="year", type="INTEGER", nullable=False, description="Year"),
        Column(name="quarter", type="INTEGER", nullable=False, description="Quarter (1-4)"),
        Column(name="month", type="INTEGER", nullable=False, description="Month (1-12)"),
        Column(name="day_of_month", type="INTEGER", nullable=False, description="Day of month (1-31)"),
        Column(name="day_of_week", type="INTEGER", nullable=False, description="Day of week (1-7, Monday=1)"),
        Column(name="is_weekend", type="BOOLEAN", nullable=False, description="Whether it's a weekend"),
        Column(name="created_at", type="TIMESTAMP", default="CURRENT_TIMESTAMP", description="Record creation timestamp"),
    ],
    indexes=[["date"], ["year", "month"]],
)

FACT_SALES = TableSchema(
    name="fact_sales",
    description="Sales fact table with foreign keys to dimensions",
    columns=[
        Column(name="sale_key", type="INTEGER", primary_key=True, nullable=False, description="Surrogate key"),
        Column(name="invoice_no", type="VARCHAR", nullable=False, description="Invoice number"),
        Column(name="invoice_date", type="VARCHAR", nullable=False, description="Invoice date string"),
        Column(name="quantity", type="INTEGER", nullable=False, description="Quantity sold"),
        Column(name="unit_price", type="DECIMAL(10, 2)", nullable=False, description="Unit price at time of sale"),
        Column(name="line_total", type="DECIMAL(12, 2)", nullable=False, description="Line total (quantity * unit_price)"),
        Column(name="customer_key", type="INTEGER", nullable=True, description="FK to dim_customer"),
        Column(name="product_key", type="INTEGER", nullable=True, description="FK to dim_product"),
        Column(name="date_key", type="INTEGER", nullable=True, description="FK to dim_date"),
        Column(name="is_return", type="BOOLEAN", default="FALSE", nullable=False, description="Whether this is a return"),
        Column(name="created_at", type="TIMESTAMP", default="CURRENT_TIMESTAMP", description="Record creation timestamp"),
    ],
    indexes=[
        ["customer_key"],
        ["product_key"],
        ["invoice_date"],
        ["date_key"],
        ["invoice_no"],
    ],
)

ALL_TABLES = [DIM_CUSTOMER, DIM_PRODUCT, DIM_DATE, FACT_SALES]

# Load order: dimensions first, then facts
LOAD_ORDER = ["dim_customer", "dim_product", "dim_date", "fact_sales"]

# Dimension table names
DIMENSION_TABLES = ["dim_customer", "dim_product", "dim_date"]
FACT_TABLE = "fact_sales"
STAGING_TABLE = "raw_transactions"


def generate_ddl(table: TableSchema) -> str:
    """Generate CREATE TABLE DDL from TableSchema."""
    columns_sql = []
    for col in table.columns:
        col_def = f"{col.name} {col.type}"
        if not col.nullable:
            col_def += " NOT NULL"
        if col.primary_key:
            col_def += " PRIMARY KEY"
        if col.default:
            col_def += f" DEFAULT {col.default}"
        columns_sql.append(col_def)

    columns_str = ",\n    ".join(columns_sql)
    return f"CREATE TABLE IF NOT EXISTS {table.name} (\n    {columns_str}\n);"


def generate_indexes(table: TableSchema) -> list[str]:
    """Generate CREATE INDEX statements from TableSchema."""
    if not table.indexes:
        return []

    statements = []
    for idx_columns in table.indexes:
        idx_name = f"idx_{table.name}_{'_'.join(idx_columns)}"
        cols_str = ", ".join(idx_columns)
        statements.append(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table.name}({cols_str});")

    return statements


def get_all_ddl() -> dict[str, str]:
    """Get all DDL statements for all tables."""
    ddl = {}
    for table in ALL_TABLES:
        ddl[table.name] = generate_ddl(table)
        for idx_sql in generate_indexes(table):
            ddl[f"idx_{table.name}_{idx_sql.split('(')[0].split('_')[-1]}"] = idx_sql
    return ddl


# SQL load statements using source column mappings
def get_load_statements() -> dict[str, str]:
    """Get SQL statements for loading dimension and fact tables."""
    src = SOURCE_COLUMNS

    return {
        "dim_customer": f"""
            INSERT INTO dim_customer (customer_key, customer_id, country)
            SELECT
                ROW_NUMBER() OVER (ORDER BY customer_id) as customer_key,
                customer_id,
                country
            FROM (
                SELECT
                    CAST("{src['customer_id']}" AS VARCHAR) as customer_id,
                    TRIM("{src['country']}") as country
                FROM {STAGING_TABLE}
                WHERE "{src['customer_id']}" IS NOT NULL
                  AND TRIM(CAST("{src['customer_id']}" AS VARCHAR)) != ''
                GROUP BY CAST("{src['customer_id']}" AS VARCHAR), TRIM("{src['country']}")
            );
        """,
        "dim_product": f"""
            INSERT INTO dim_product (product_key, stock_code, description, unit_price)
            SELECT
                ROW_NUMBER() OVER (ORDER BY stock_code) as product_key,
                stock_code,
                description,
                unit_price
            FROM (
                SELECT DISTINCT
                    "{src['stock_code']}" as stock_code,
                    "{src['description']}" as description,
                    CAST("{src['unit_price']}" AS DECIMAL(10, 2)) as unit_price
                FROM {STAGING_TABLE}
                WHERE "{src['description']}" IS NOT NULL
                  AND TRIM(CAST("{src['description']}" AS VARCHAR)) != ''
            );
        """,
        "dim_date": f"""
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
                    CAST(strptime("{src['invoice_date']}", '%m/%d/%Y %H:%M') AS DATE) as date_str
                FROM {STAGING_TABLE}
                WHERE "{src['invoice_date']}" IS NOT NULL
            );
        """,
        "fact_sales": f"""
            INSERT INTO fact_sales (sale_key, invoice_no, invoice_date, quantity, unit_price, line_total, customer_key, product_key, date_key, is_return)
            SELECT
                ROW_NUMBER() OVER (ORDER BY t."{src['invoice_no']}", t."{src['stock_code']}") as sale_key,
                t."{src['invoice_no']}" as invoice_no,
                CAST(t."{src['invoice_date']}" AS VARCHAR) as invoice_date,
                CAST(t."{src['quantity']}" AS INTEGER) as quantity,
                CAST(t."{src['unit_price']}" AS DECIMAL(10, 2)) as unit_price,
                CAST(t."{src['quantity']}" * t."{src['unit_price']}" AS DECIMAL(12, 2)) as line_total,
                c.customer_key,
                p.product_key,
                CAST(REPLACE(CAST(DATE(strptime(t."{src['invoice_date']}", '%m/%d/%Y %H:%M')) AS VARCHAR), '-', '') AS INTEGER) as date_key,
                CASE WHEN CAST(t."{src['quantity']}" AS INTEGER) < 0 THEN TRUE ELSE FALSE END as is_return
            FROM {STAGING_TABLE} t
            JOIN dim_customer c ON CAST(t."{src['customer_id']}" AS VARCHAR) = c.customer_id
            JOIN dim_product p ON t."{src['stock_code']}" = p.stock_code
            WHERE t."{src['customer_id']}" IS NOT NULL
              AND TRIM(CAST(t."{src['customer_id']}" AS VARCHAR)) != ''
              AND t."{src['description']}" IS NOT NULL
              AND TRIM(CAST(t."{src['description']}" AS VARCHAR)) != ''
              AND t."{src['invoice_no']}" IS NOT NULL
              AND TRIM(CAST(t."{src['invoice_no']}" AS VARCHAR)) != '';
        """,
    }


# Validation queries
VALIDATION_QUERIES = {
    "dim_customer_count": "SELECT COUNT(*) as count FROM dim_customer;",
    "dim_product_count": "SELECT COUNT(*) as count FROM dim_product;",
    "dim_date_count": "SELECT COUNT(*) as count FROM dim_date;",
    "fact_sales_count": "SELECT COUNT(*) as count FROM fact_sales;",
    "fact_sales_null_keys": "SELECT COUNT(*) as null_count FROM fact_sales WHERE customer_key IS NULL OR product_key IS NULL OR date_key IS NULL;",
    "fact_sales_returns": "SELECT COUNT(*) as return_count FROM fact_sales WHERE is_return = TRUE;",
    "fact_sales_negative_qty": "SELECT COUNT(*) as neg_count FROM fact_sales WHERE quantity < 0;",
}

# Summary display configuration
SUMMARY_FIELDS = [
    {"key": "dim_customer_count", "label": "Customers"},
    {"key": "dim_product_count", "label": "Products"},
    {"key": "dim_date_count", "label": "Dates"},
    {"key": "fact_sales_count", "label": "Sales"},
]

SUMMARY_EXTRA_FIELDS = [
    {"key": "fact_sales_returns", "label": "Returns"},
    {"key": "fact_sales_null_keys", "label": "Null FKs"},
]

# Cleaning rules
CLEANING_RULES = [
    {"column": SOURCE_COLUMNS["customer_id"], "description": "null CustomerID"},
    {"column": SOURCE_COLUMNS["description"], "description": "null Description"},
    {"column": SOURCE_COLUMNS["invoice_no"], "description": "null InvoiceNo"},
]
