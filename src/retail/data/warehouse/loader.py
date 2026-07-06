"""
Data warehouse loader for the dimensional model.
"""

from pathlib import Path
import polars as pl
from sqlalchemy import create_engine, select, delete
from retail.config.settings import settings
from retail.data.warehouse.models import Base, DimCustomer, DimProduct, FactSales

def load_data() -> None:
    """
    Load cleaned data from the staging area into the data warehouse.
    This function:
    1. Creates the database and tables if they don't exist.
    2. Loads the cleaned Parquet file.
    3. Truncates existing data (for a full refresh).
    4. Inserts dimension data (customers and products).
    5. Inserts fact data (sales) with foreign key references.
    """
    # Create database engine
    engine = create_engine(f"duckdb:///{settings.DUCKDB_DATABASE_PATH}")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Load cleaned data
    cleaned_data_path = settings.DATA_STAGING_PATH / "online_retail_clean.parquet"
    df = pl.read_parquet(cleaned_data_path)
    
    # Begin transaction
    with engine.begin() as conn:
        # Clear existing data (in reverse order of foreign keys)
        conn.execute(delete(FactSales))
        conn.execute(delete(DimCustomer))
        conn.execute(delete(DimProduct))
        
        # Insert dimension data
        # Customers
        customers_df = df.select(['CustomerID', 'Country']).unique()
        customer_records = [
            {"customer_id": row.CustomerID, "country": row.Country}
            for row in customers_df.iter_rows(named=True)
        ]
        if customer_records:
            conn.execute(DimCustomer.__table__.insert(), customer_records)
        
        # Products
        products_df = df.select(['StockCode', 'Description', 'UnitPrice']).unique()
        product_records = [
            {"stock_code": row.StockCode, "description": row.Description, "unit_price": row.UnitPrice}
            for row in products_df.iter_rows(named=True)
        ]
        if product_records:
            conn.execute(DimProduct.__table__.insert(), product_records)
        
        # Prepare fact data by joining with dimension tables to get keys
        # We'll load the dimension tables into DataFrames for joining
        customer_df = pl.read_database(
            query="SELECT customer_key, customer_id, country FROM dim_customer",
            connection=engine.connection()
        )
        product_df = pl.read_database(
            query="SELECT product_key, stock_code, description, unit_price FROM dim_product",
            connection=engine.connection()
        )
        
        # Join to get keys
        fact_df = df.join(
            customer_df, left_on="CustomerID", right_on="customer_id", how="left"
        ).join(
            product_df, left_on="StockCode", right_on="stock_code", how="left"
        ).select([
            "customer_key",
            "product_key",
            "InvoiceNo",
            "InvoiceDate",
            "Quantity",
            "UnitPrice",
            "LineTotal"
        ]).rename({
            "InvoiceNo": "invoice_no",
            "InvoiceDate": "invoice_date",
            "Quantity": "quantity",
            "UnitPrice": "unit_price",
            "LineTotal": "line_total"
        })
        
        # Insert fact data
        fact_records = fact_df.to_dicts()
        if fact_records:
            conn.execute(FactSales.__table__.insert(), fact_records)
    
    print(f"Loaded {len(df)} rows into the data warehouse.")

if __name__ == "__main__":
    load_data()