"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_retail_data():
    """Create sample retail data for testing."""
    import polars as pl
    return pl.DataFrame({
        "InvoiceNo": ["536365", "536365", "536367"],
        "StockCode": ["85123A", "71053", "84406B"],
        "Description": ["WHITE HANGING HEART HAIR CLIP", "RED BLOSSOM BROOCH", "RECYCLED CANDLES"],
        "Quantity": [6, 6, 1],
        "InvoiceDate": ["2010-12-01 14:00:00", "2010-12-01 14:00:00", "2010-12-01 14:00:00"],
        "UnitPrice": [2.05, 3.85, 2.05],
        "CustomerID": [17850, 17850, 17850],
        "Country": ["United Kingdom", "United Kingdom", "United Kingdom"]
    })