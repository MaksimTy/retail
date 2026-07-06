"""
UCI ML Repository Downloader for Online Retail Dataset (ID: 352)
"""

from ucimlrepo import fetch_ucirepo 
import polars as pl
from pathlib import Path
from retail.config.settings import settings

def download_online_retail() -> pl.DataFrame:
    """
    Fetch the Online Retail dataset from UCI ML Repository (ID: 352)
    and return as a Polars DataFrame.
    """
    # Fetch dataset 
    online_retail = fetch_ucirepo(id=352) 
    
    # Features and targets
    X = online_retail.data.features 
    y = online_retail.data.targets 
    
    # Combine features and target if needed
    # The dataset has one table with all columns
    df = pl.from_pandas(X)  # Assuming X is pandas DataFrame
    
    # Save raw data to staging area
    raw_data_path = settings.DATA_SOURCE_PATH / "online_retail_raw.parquet"
    raw_data_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(raw_data_path)
    
    return df

if __name__ == "__main__":
    df = download_online_retail()
    print(f"Downloaded dataset with shape: {df.shape}")