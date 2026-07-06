# Retail AI Agent Ontology Guide

## Overview

The Ontology layer is the core of the OAG (Ontology-Augmented Generation) architecture. It defines the business concepts, metrics, and relationships that enable the AI agent to understand and query the data warehouse.

## Core Concepts

### Customer
- **Description**: A customer who makes purchases
- **Attributes**:
  - `customer_key`: Primary key (surrogate key)
  - `customer_id`: Unique identifier for the customer
  - `country`: Country where the customer resides

### Product
- **Description**: A product that can be purchased
- **Attributes**:
  - `product_key`: Primary key (surrogate key)
  - `stock_code`: Unique code for the product
  - `description`: Description of the product
  - `unit_price`: Price per unit of the product

### Order (Invoice)
- **Description**: A customer order (invoice)
- **Attributes**:
  - `sale_key`: Primary key (surrogate key)
  - `customer_key`: Foreign key to dim_customer
  - `product_key`: Foreign key to dim_product
  - `invoice_no`: Unique identifier for the order
  - `invoice_date`: Date and time when the order was placed
  - `quantity`: Number of items ordered
  - `unit_price`: Price per unit at the time of order
  - `line_total`: Total value of the line item (quantity × unit_price)

## Metrics

### Total Revenue
- **Definition**: Sum of all line totals in the fact_sales table
- **SQL**: `SELECT SUM(line_total) FROM fact_sales`

### Order Count
- **Definition**: Number of unique invoices
- **SQL**: `SELECT COUNT(DISTINCT invoice_no) FROM fact_sales`

### Average Order Value (AOV)
- **Definition**: Total revenue divided by number of orders
- **SQL**: `SELECT SUM(line_total) / COUNT(DISTINCT invoice_no) FROM fact_sales`

### Customer Count
- **Definition**: Number of unique customers
- **SQL**: `SELECT COUNT(*) FROM dim_customer`

### Product Count
- **Definition**: Number of unique products
- **SQL**: `SELECT COUNT(*) FROM dim_product`

## Relationships

The entity relationship graph defines how tables are connected:

```
dim_customer ──< fact_sales >── dim_product
     │                               │
     └── customer_key (FK)           └── product_key (FK)
```

## Extending the Ontology

To add new concepts or metrics:

1. Add the definition to `src/retail/ontology/concepts/definitions.yaml`
2. Update the `ConceptRegistry` in `src/retail/ontology/concepts/registry.py`
3. Add new few-shot examples to `src/retail/ontology/query_builder/prompts.py`
4. Update the SQL validator if needed

## Example Questions

The following questions can be answered using the current ontology:

- "What is the total revenue?"
- "How many orders are there?"
- "What is the total revenue by country?"
- "List the top 5 products by revenue."
- "How many customers are there in each country?"
- "What is the average order value?"
- "Which products have the highest total quantity sold?"