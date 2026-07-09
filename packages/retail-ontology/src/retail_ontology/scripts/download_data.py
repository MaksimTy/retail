"""
UCI Online Retail Dataset Downloader.

Downloads the Online Retail dataset (UCI ID: 352) from the UCI Machine Learning Repository
and saves it to the local data directory.

Usage:
    python -m retail_ontology.scripts.download_data
    retail-download
"""

import logging
import sys
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DownloadConfig(BaseModel):
    """Configuration for data download."""

    uci_dataset_id: int = Field(default=352, description="UCI dataset ID for Online Retail")
    data_url: str = Field(
        default="https://archive.ics.uci.edu/static/public/352/data.csv",
        description="Direct URL to the dataset CSV"
    )
    output_dir: Path = Field(default=Path("./data"), description="Output directory for downloaded data")
    output_filename: str = Field(default="online_retail.csv", description="Output filename")


def download_uci_dataset(config: DownloadConfig) -> pd.DataFrame:
    """
    Download dataset directly from UCI Machine Learning Repository.

    Args:
        config: Download configuration

    Returns:
        DataFrame with the dataset
    """
    logger.info(f"Fetching UCI dataset ID {config.uci_dataset_id} from {config.data_url}")

    # Download directly from UCI URL
    df = pd.read_csv(config.data_url)

    logger.info(f"Downloaded dataset with {len(df)} rows and {len(df.columns)} columns")
    logger.info(f"Columns: {list(df.columns)}")

    return df


def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate the downloaded DataFrame.

    Args:
        df: DataFrame to validate

    Returns:
        True if valid, raises ValueError otherwise
    """
    required_columns = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if len(df) == 0:
        raise ValueError("Dataset is empty")

    logger.info("DataFrame validation passed")
    return True


def save_dataframe(df: pd.DataFrame, config: DownloadConfig) -> Path:
    """
    Save DataFrame to CSV file.

    Args:
        df: DataFrame to save
        config: Download configuration

    Returns:
        Path to saved file
    """
    # Create output directory if it doesn't exist
    config.output_dir.mkdir(parents=True, exist_ok=True)

    output_path = config.output_dir / config.output_filename

    # Save to CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Saved dataset to {output_path}")

    return output_path


def main() -> None:
    """Main entry point for data download."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create config
    config = DownloadConfig()

    try:
        # Download dataset
        df = download_uci_dataset(config)

        # Validate
        validate_dataframe(df)

        # Save
        output_path = save_dataframe(df, config)

        # Print summary
        print(f"\n{'='*60}")
        print("Download completed successfully!")
        print(f"{'='*60}")
        print(f"Dataset: UCI ID {config.uci_dataset_id}")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Saved to: {output_path}")
        print(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
