"""
Data warehouse module.
"""

from retail.data.warehouse.models import DimCustomer, DimProduct, FactSales, Base
from retail.data.warehouse.loader import load_data

__all__ = ["DimCustomer", "DimProduct", "FactSales", "Base", "load_data"]