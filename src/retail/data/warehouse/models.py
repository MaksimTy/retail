"""
SQLAlchemy models for the dimensional model.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Dimension table for customers
class DimCustomer(Base):
    __tablename__ = 'dim_customer'

    customer_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), nullable=False)
    country = Column(String(50))

# Dimension table for products
class DimProduct(Base):
    __tablename__ = 'dim_product'

    product_key = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(50), nullable=False)
    description = Column(String(255))
    unit_price = Column(Float)

# Fact table for sales
class FactSales(Base):
    __tablename__ = 'fact_sales'

    sale_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_key = Column(Integer, ForeignKey('dim_customer.customer_key'), nullable=False)
    product_key = Column(Integer, ForeignKey('dim_product.product_key'), nullable=False)
    invoice_no = Column(String(50), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)