"""
DuckDB Warehouse Builder.

ETL pipeline that transforms raw UCI Online Retail data into a dimensional model
in DuckDB. Implements Kimball dimensional modeling with surrogate keys.

Usage:
    python -m retail_ontology.scripts.build_warehouse
    retail-build
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WarehouseConfig(BaseModel):
    """Configuration for warehouse building."""

    data_path: Path = Field(default=Path("./data/online_retail.csv"), description="Path to raw data CSV")
    duckdb_path: Path = Field(default=Path("./data/warehouse.duckdb"), description="Path to DuckDB database")
    batch_size: int = Field(default=10000, description="Batch size for data insertion")


# SQL DDL for dimensional model
DDL_SCHEMA = """
-- Dimension: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY,
    stock_code VARCHAR,
    description VARCHAR,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Date (for time analysis)
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

-- Fact: Sales
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_invoice_date ON fact_sales(invoice_date);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key ON fact_sales(date_key);
"""


def load_raw_data(config: WarehouseConfig) -> pd.DataFrame:
    """
    Load raw data from CSV file.

    Args:
        config: Warehouse configuration

    Returns:
        DataFrame with raw data
    """
    logger.info(f"Loading raw data from {config.data_path}")

    if not config.data_path.exists():
        raise FileNotFoundError(f"Data file not found: {config.data_path}")

    df = pd.read_csv(config.data_path)
    logger.info(f"Loaded {len(df)} rows from raw data")

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data by handling nulls, duplicates, and data quality issues.

    Args:
        df: Raw DataFrame

    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning...")

    initial_count = len(df)

    # Remove rows with null CustomerID (these are likely cancelled orders)
    df = df.dropna(subset=["CustomerID"])
    logger.info(f"Removed {initial_count - len(df)} rows with null CustomerID")

    # Remove rows with null Description (likely returns or invalid data)
    df = df.dropna(subset=["Description"])
    logger.info(f"Removed {initial_count - len(df)} rows with null Description")

    # Remove rows with null InvoiceNo
    df = df.dropna(subset=["InvoiceNo"])
    logger.info(f"Removed {initial_count - len(df)} rows with null InvoiceNo")

    # Remove duplicates
    df = df.drop_duplicates()
    logger.info(f"Removed {initial_count - len(df)} duplicate rows")

    # Parse InvoiceDate
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Convert CustomerID to integer
    df["CustomerID"] = df["CustomerID"].astype(int)

    # Calculate line_total
    df["line_total"] = df["Quantity"] * df["UnitPrice"]

    # Identify returns (negative quantities)
    df["is_return"] = df["Quantity"] < 0

    # Standardize country names
    df["Country"] = df["Country"].str.strip()

    logger.info(f"Data cleaning complete. Final row count: {len(df)}")

    return df


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build date dimension table.

    Args:
        df: Cleaned DataFrame with InvoiceDate

    Returns:
        Date dimension DataFrame
    """
    logger.info("Building date dimension...")

    # Extract unique dates
    dates = df["InvoiceDate"].dt.date.unique()

    dim_date = pd.DataFrame({"date": dates})
    # Convert date to string for proper DuckDB handling
    dim_date["date"] = dim_date["date"].astype(str)
    dim_date["date_key"] = dim_date["date"].apply(lambda x: int(x.replace("-", "")))
    dim_date["year"] = dim_date["date"].apply(lambda x: int(x[:4]))
    dim_date["month"] = dim_date["date"].apply(lambda x: int(x[5:7]))
    dim_date["day_of_month"] = dim_date["date"].apply(lambda x: int(x[8:10]))
    dim_date["quarter"] = dim_date["month"].apply(lambda x: (x - 1) // 3 + 1)
    dim_date["day_of_week"] = pd.to_datetime(dim_date["date"]).dt.dayofweek + 1
    dim_date["is_weekend"] = dim_date["day_of_week"].isin([6, 7])

    logger.info(f"Built date dimension with {len(dim_date)} rows")

    return dim_date


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build customer dimension table with surrogate keys.

    Args:
        df: Cleaned DataFrame

    Returns:
        Customer dimension DataFrame
    """
    logger.info("Building customer dimension...")

    # Get unique customers
    customers = df[["CustomerID", "Country"]].drop_duplicates()

    # Create surrogate key
    customers = customers.reset_index(drop=True)
    customers["customer_key"] = customers.index + 1

    # Rename columns
    dim_customer = customers.rename(columns={"CustomerID": "customer_id", "Country": "country"})

    # Reorder columns
    dim_customer = dim_customer[["customer_key", "customer_id", "country"]]

    logger.info(f"Built customer dimension with {len(dim_customer)} rows")

    return dim_customer


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build product dimension table with surrogate keys.

    Args:
        df: Cleaned DataFrame

    Returns:
        Product dimension DataFrame
    """
    logger.info("Building product dimension...")

    # Get unique products
    products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates()

    # Create surrogate key
    products = products.reset_index(drop=True)
    products["product_key"] = products.index + 1

    # Rename columns
    dim_product = products.rename(columns={"StockCode": "stock_code", "Description": "description", "UnitPrice": "unit_price"})

    # Reorder columns
    dim_product = dim_product[["product_key", "stock_code", "description", "unit_price"]]

    logger.info(f"Built product dimension with {len(dim_product)} rows")

    return dim_product


def build_fact_sales(df: pd.DataFrame, dim_customer: pd.DataFrame, dim_product: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact sales table with foreign keys.

    Args:
        df: Cleaned DataFrame
        dim_customer: Customer dimension
        dim_product: Product dimension
        dim_date: Date dimension

    Returns:
        Fact sales DataFrame
    """
    logger.info("Building fact sales table...")

    # Create lookup dictionaries
    customer_lookup = dim_customer.set_index("customer_id")["customer_key"].to_dict()
    product_lookup = dim_product.set_index("stock_code")["product_key"].to_dict()
    date_lookup = dim_date.set_index("date")["date_key"].to_dict()

    # Add foreign keys
    df = df.copy()
    df["customer_key"] = df["CustomerID"].map(customer_lookup)
    df["product_key"] = df["StockCode"].map(product_lookup)
    # Convert date to string format for lookup
    df["date_str"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d")
    df["date_key"] = df["date_str"].map(date_lookup)

    # Create sale_key
    df = df.reset_index(drop=True)
    df["sale_key"] = df.index + 1

    # Select and rename columns for fact table
    fact_sales = df[[
        "sale_key", "InvoiceNo", "InvoiceDate", "Quantity", "UnitPrice",
        "line_total", "customer_key", "product_key", "date_key", "is_return"
    ]].copy()

    fact_sales = fact_sales.rename(columns={
        "InvoiceNo": "invoice_no",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price"
    })

    # Convert invoice_date to string format
    fact_sales["invoice_date"] = fact_sales["invoice_date"].dt.strftime("%Y-%m-%d")

    # Convert is_return to boolean
    fact_sales["is_return"] = fact_sales["is_return"].astype(bool)

    logger.info(f"Built fact sales table with {len(fact_sales)} rows")

    return fact_sales


def create_duckdb_connection(config: WarehouseConfig) -> duckdb.DuckDBPyConnection:
    """
    Create DuckDB connection and initialize schema.

    Args:
        config: Warehouse configuration

    Returns:
        DuckDB connection
    """
    logger.info(f"Connecting to DuckDB at {config.duckdb_path}")

    # Create data directory if it doesn't exist
    config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB
    conn = duckdb.connect(str(config.duckdb_path))

    # Create schema
    conn.execute(DDL_SCHEMA)

    logger.info("DuckDB schema created")

    return conn


def load_data_to_duckdb(conn: duckdb.DuckDBPyConnection, dim_date: pd.DataFrame, dim_customer: pd.DataFrame,
                         dim_product: pd.DataFrame, fact_sales: pd.DataFrame) -> None:
    """
    Load dimension and fact tables to DuckDB.

    Args:
        conn: DuckDB connection
        dim_date: Date dimension
        dim_customer: Customer dimension
        dim_product: Product dimension
        fact_sales: Fact sales table
    """
    logger.info("Loading data to DuckDB...")

    # Register DataFrames as temporary tables
    conn.register("temp_dim_date", dim_date)
    conn.register("temp_dim_customer", dim_customer)
    conn.register("temp_dim_product", dim_product)
    conn.register("temp_fact_sales", fact_sales)

    # Load date dimension with explicit column selection
    conn.execute("DELETE FROM dim_date")
    conn.execute("""
        INSERT INTO dim_date (date_key, date, year, quarter, month, day_of_month, day_of_week, is_weekend)
        SELECT date_key, date, year, quarter, month, day_of_month, day_of_week, is_weekend FROM temp_dim_date
    """)
    logger.info(f"Loaded {len(dim_date)} rows to dim_date")

    # Load customer dimension
    conn.execute("DELETE FROM dim_customer")
    conn.execute("""
        INSERT INTO dim_customer (customer_key, customer_id, country)
        SELECT customer_key, customer_id, country FROM temp_dim_customer
    """)
    logger.info(f"Loaded {len(dim_customer)} rows to dim_customer")

    # Load product dimension
    conn.execute("DELETE FROM dim_product")
    conn.execute("""
        INSERT INTO dim_product (product_key, stock_code, description, unit_price)
        SELECT product_key, stock_code, description, unit_price FROM temp_dim_product
    """)
    logger.info(f"Loaded {len(dim_product)} rows to dim_product")

    # Load fact sales with explicit column selection
    conn.execute("DELETE FROM fact_sales")
    conn.execute("""
        INSERT INTO fact_sales (sale_key, invoice_no, invoice_date, quantity, unit_price, line_total,
                                customer_key, product_key, date_key, is_return)
        SELECT sale_key, invoice_no, invoice_date, quantity, unit_price, line_total,
               customer_key, product_key, date_key, is_return FROM temp_fact_sales
    """)
    logger.info(f"Loaded {len(fact_sales)} rows to fact_sales")

    # Drop temporary views (registered via conn.register)
    conn.execute("DROP VIEW IF EXISTS temp_dim_date")
    conn.execute("DROP VIEW IF EXISTS temp_dim_customer")
    conn.execute("DROP VIEW IF EXISTS temp_dim_product")
    conn.execute("DROP VIEW IF EXISTS temp_fact_sales")


def validate_warehouse(conn: duckdb.DuckDBPyConnection) -> bool:
    """
    Validate the warehouse by checking row counts and referential integrity.

    Args:
        conn: DuckDB connection

    Returns:
        True if validation passes
    """
    logger.info("Validating warehouse...")

    # Check row counts
    result = conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()
    customer_count = result[0]
    logger.info(f"dim_customer: {customer_count} rows")

    result = conn.execute("SELECT COUNT(*) FROM dim_product").fetchone()
    product_count = result[0]
    logger.info(f"dim_product: {product_count} rows")

    result = conn.execute("SELECT COUNT(*) FROM dim_date").fetchone()
    date_count = result[0]
    logger.info(f"dim_date: {date_count} rows")

    result = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()
    sales_count = result[0]
    logger.info(f"fact_sales: {sales_count} rows")

    # Check referential integrity
    result = conn.execute("""
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE c.customer_key IS NULL
    """).fetchone()
    orphan_customers = result[0]
    if orphan_customers > 0:
        logger.warning(f"Found {orphan_customers} orphan customer references in fact_sales")

    result = conn.execute("""
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_product p ON f.product_key = p.product_key
        WHERE p.product_key IS NULL
    """).fetchone()
    orphan_products = result[0]
    if orphan_products > 0:
        logger.warning(f"Found {orphan_products} orphan product references in fact_sales")

    result = conn.execute("""
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """).fetchone()
    orphan_dates = result[0]
    if orphan_dates > 0:
        logger.warning(f"Found {orphan_dates} orphan date references in fact_sales")

    # Check for null values in fact table
    result = conn.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE customer_key IS NULL OR product_key IS NULL OR date_key IS NULL
    """).fetchone()
    null_keys = result[0]
    if null_keys > 0:
        logger.warning(f"Found {null_keys} rows with null foreign keys in fact_sales")

    logger.info("Warehouse validation complete")

    return True


def print_summary(conn: duckdb.DuckDBPyConnection) -> None:
    """Print summary statistics from the warehouse."""
    print(f"\n{'='*60}")
    print("Warehouse Build Summary")
    print(f"{'='*60}")

    # Total revenue
    result = conn.execute("SELECT SUM(line_total) FROM fact_sales WHERE is_return = FALSE").fetchone()
    total_revenue = result[0] if result[0] else 0
    print(f"Total Revenue: ${total_revenue:,.2f}")

    # Number of transactions
    result = conn.execute("SELECT COUNT(*) FROM fact_sales WHERE is_return = FALSE").fetchone()
    transactions = result[0] if result[0] else 0
    print(f"Number of Transactions: {transactions:,}")

    # Number of customers
    result = conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()
    customers = result[0] if result[0] else 0
    print(f"Number of Customers: {customers:,}")

    # Number of products
    result = conn.execute("SELECT COUNT(*) FROM dim_product").fetchone()
    products = result[0] if result[0] else 0
    print(f"Number of Products: {products:,}")

    # Top 5 countries by revenue
    print(f"\nTop 5 Countries by Revenue:")
    result = conn.execute("""
        SELECT c.country, SUM(f.line_total) as revenue
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE f.is_return = FALSE
        GROUP BY c.country
        ORDER BY revenue DESC
        LIMIT 5
    """).fetchall()
    for country, revenue in result:
        print(f"  {country}: ${revenue:,.2f}")

    print(f"{'='*60}\n")


def main() -> None:
    """Main entry point for warehouse building."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create config
    config = WarehouseConfig()

    try:
        # Load raw data
        df = load_raw_data(config)

        # Clean data
        df = clean_data(df)

        # Build dimensions
        dim_date = build_dim_date(df)
        dim_customer = build_dim_customer(df)
        dim_product = build_dim_product(df)

        # Build fact table
        fact_sales = build_fact_sales(df, dim_customer, dim_product, dim_date)

        # Create DuckDB connection and schema
        conn = create_duckdb_connection(config)

        # Load data to DuckDB
        load_data_to_duckdb(conn, dim_date, dim_customer, dim_product, fact_sales)

        # Validate warehouse
        validate_warehouse(conn)

        # Print summary
        print_summary(conn)

        # Close connection
        conn.close()

        print(f"Warehouse built successfully at {config.duckdb_path}")

    except Exception as e:
        logger.error(f"Failed to build warehouse: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
