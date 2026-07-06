"""
Data cleaning module for the Online Retail dataset.
"""

import polars as pl
from pathlib import Path
from retail.config.settings import settings

def clean_online_retail(df: pl.DataFrame) -> pl.DataFrame:
    """
    Clean the Online Retail dataset.
    Steps:
    1. Remove rows with missing InvoiceNo or StockCode
    2. Remove rows where Quantity or UnitPrice is not positive (if applicable)
    3. Convert InvoiceDate to datetime
    4. Calculate LineTotal (Quantity * UnitPrice)
    5. Remove duplicates
    6. Filter out cancelled invoices (those starting with 'C')
    """
    # Make a copy to avoid modifying the original
    df_clean = df.clone()
    
    # 1. Remove rows with missing InvoiceNo or StockCode
    df_clean = df_clean.filter(
        pl.col("InvoiceNo").is_not_null() & 
        pl.col("StockCode").is_not_null()
    )
    
    # 2. Remove rows where Quantity or UnitPrice is not positive (if applicable)
    # Note: The dataset has some negative values for returns, but we'll keep them for now
    # as they represent returns. We'll filter out cancelled invoices later.
    
    # 3. Convert InvoiceDate to datetime
    df_clean = df_clean.with_columns(
        pl.col("InvoiceDate").str.strptime(pl.Datetime, "%m/%d/%Y %H:%M")
    )
    
    # 4. Calculate LineTotal
    df_clean = df_clean.with_columns(
        (pl.col("Quantity") * pl.col("UnitPrice")).alias("LineTotal")
    )
    
    # 5. Remove duplicates
    df_clean = df_clean.unique()
    
    # 6. Filter out cancelled invoices (InvoiceNo starts with 'C')
    df_clean = df_clean.filter(~pl.col("InvoiceNo").str.starts_with("C"))
    
    return df_clean

def clean_and_save() -> None:
    """
    Main function to read raw data, clean it, and save to staging area.
    """
    # Read raw data
    raw_data_path = settings.DATA_SOURCE_PATH / "online_retail_raw.parquet"
    df = pl.read_parquet(raw_data_path)
    
    # Clean data
    df_clean = clean_online_retail(df)
    
    # Save cleaned data to staging area
    staging_path = settings.DATA_STAGING_PATH / "online_retail_clean.parquet"
    staging_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.write_parquet(staging_path)
    
    print(f"Cleaned dataset saved to {staging_path} with shape: {df_clean.shape}")

if __name__ == "__main__":
    clean_and_save()