"""
Repository pattern for typed data access.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from retail.data.warehouse.models import DimCustomer, DimProduct, FactSales

class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, customer_id: int) -> Optional[DimCustomer]:
        return self.session.query(DimCustomer).filter(DimCustomer.customer_key == customer_id).first()
    
    def get_by_customer_id(self, customer_id: str) -> Optional[DimCustomer]:
        return self.session.query(DimCustomer).filter(DimCustomer.customer_id == customer_id).first()
    
    def list_by_country(self, country: str) -> List[DimCustomer]:
        return self.session.query(DimCustomer).filter(DimCustomer.country == country).all()
    
    def get_customer_sales(self, customer_id: int) -> List[FactSales]:
        return self.session.query(FactSales).filter(FactSales.customer_key == customer_id).all()

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, product_id: int) -> Optional[DimProduct]:
        return self.session.query(DimProduct).filter(DimProduct.product_key == product_id).first()
    
    def get_by_stock_code(self, stock_code: str) -> Optional[DimProduct]:
        return self.session.query(DimProduct).filter(DimProduct.stock_code == stock_code).first()
    
    def search_by_description(self, term: str) -> List[DimProduct]:
        return self.session.query(DimProduct).filter(DimProduct.description.ilike(f"%{term}%")).all()
    
    def get_product_sales(self, product_id: int) -> List[FactSales]:
        return self.session.query(FactSales).filter(FactSales.product_key == product_id).all()

class SalesRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, sale_id: int) -> Optional[FactSales]:
        return self.session.query(FactSales).filter(FactSales.sale_key == sale_id).first()
    
    def get_by_invoice_no(self, invoice_no: str) -> List[FactSales]:
        return self.session.query(FactSales).filter(FactSales.invoice_no == invoice_no).all()
    
    def get_sales_by_date_range(self, start_date, end_date) -> List[FactSales]:
        return self.session.query(FactSales).filter(
            FactSales.invoice_date >= start_date,
            FactSales.invoice_date <= end_date
        ).all()
    
    def get_total_revenue(self) -> float:
        result = self.session.query(func.sum(FactSales.line_total)).scalar()
        return float(result) if result else 0.0
    
    def get_revenue_by_country(self) -> List[Dict[str, Any]]:
        result = self.session.query(
            DimCustomer.country,
            func.sum(FactSales.line_total).label('total_revenue')
        ).join(FactSales.customer_key).group_by(DimCustomer.country).all()
        return [{"country": row.country, "total_revenue": float(row.total_revenue)} for row in result]
    
    def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        result = self.session.query(
            DimProduct.stock_code,
            DimProduct.description,
            func.sum(FactSales.quantity).label('total_quantity'),
            func.sum(FactSales.line_total).label('total_revenue')
        ).join(FactSales.product_key).group_by(
            DimProduct.stock_code,
            DimProduct.description
        ).order_by(func.sum(FactSales.line_total).desc()).limit(limit).all()
        return [
            {
                "stock_code": row.stock_code,
                "description": row.description,
                "total_quantity": int(row.total_quantity),
                "total_revenue": float(row.total_revenue)
            }
            for row in result
        ]