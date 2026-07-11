# Ontology Guide

## Retail Ontology Platform - How to Define Concepts and Metrics

This guide explains how to define business concepts and metrics for the Retail Ontology Platform.

## Table of Contents

1. [Introduction](#introduction)
2. [Concepts](#concepts)
3. [Metrics](#metrics)
4. [Relationships](#relationships)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

---

## Introduction

The Retail Ontology Platform uses a semantic layer to bridge natural language questions with database queries. This is achieved through:

- **Concepts**: Business entities (dimensions) with attributes
- **Metrics**: Business measurements with expressions
- **Relationships**: Join paths between entities

---

## Concepts

### What is a Concept?

A concept represents a business entity in your data model. Each concept maps to a database table and defines:

- Primary key
- Attributes (columns)
- Foreign keys (relationships to other concepts)
- Display name and description

### Concept Definition Structure

```yaml
concepts:
  concept_name:
    table: table_name
    primary_key: column_name
    display_name: "Human Readable Name"
    description: "Optional description"
    attributes:
      - name: column_name
        type: string|integer|decimal|datetime|boolean
        description: "Column description"
        foreign_key: other_table.other_column  # Optional
```

### Attribute Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text data | "United Kingdom" |
| `integer` | Whole numbers | 12345 |
| `decimal` | Fixed-point numbers | 1234.56 |
| `datetime` | Date/time values | "2024-01-15" |
| `boolean` | True/false values | true |

### Example: Customer Concept

```yaml
concepts:
  customer:
    table: dim_customer
    primary_key: customer_key
    display_name: "Customer"
    description: "Customer dimension table"
    attributes:
      - name: customer_key
        type: integer
        description: "Surrogate key for customer"
      - name: customer_id
        type: string
        description: "Original customer ID from source system"
      - name: country
        type: string
        description: "Customer country"
      - name: currency
        type: string
        description: "Customer currency"
```

### Example: Product Concept

```yaml
concepts:
  product:
    table: dim_product
    primary_key: product_key
    display_name: "Product"
    description: "Product dimension table"
    attributes:
      - name: product_key
        type: integer
        description: "Surrogate key for product"
      - name: stock_code
        type: string
        description: "Product stock code"
      - name: description
        type: string
        description: "Product description"
      - name: category
        type: string
        description: "Product category"
      - name: unit_price
        type: decimal
        description: "Current unit price"
```

### Example: Sale Fact Concept

```yaml
concepts:
  sale:
    table: fact_sales
    primary_key: sale_key
    display_name: "Sale"
    description: "Sales fact table"
    attributes:
      - name: sale_key
        type: integer
        description: "Surrogate key for sale"
      - name: invoice_no
        type: string
        description: "Invoice number"
      - name: invoice_date
        type: datetime
        description: "Invoice date"
      - name: quantity
        type: integer
        description: "Quantity sold"
      - name: unit_price
        type: decimal
        description: "Unit price at time of sale"
      - name: line_total
        type: decimal
        description: "Total amount (quantity * unit_price)"
      - name: customer_key
        type: integer
        description: "FK to dim_customer"
        foreign_key: dim_customer.customer_key
      - name: product_key
        type: integer
        description: "FK to dim_product"
        foreign_key: dim_product.product_key
      - name: date_key
        type: integer
        description: "FK to dim_date"
        foreign_key: dim_date.date_key
```

---

## Metrics

### What is a Metric?

A metric defines a business measurement that can be computed from your data. Each metric specifies:

- Name and description
- Expression (SQL-like)
- Grain (level of detail)
- Format (currency, number, percentage)
- Dependencies (other metrics)

### Metric Definition Structure

```yaml
metrics:
  metric_name:
    name: "Display Name"
    expression: "SQL expression"
    grain: [dimension1, dimension2]  # Optional
    format: currency|number|percentage
    description: "Metric description"
    dependencies:  # Optional
      - dependent_metric: "expression"
```

### Expression Syntax

Expressions use a SQL-like syntax with table aliases:

- `fact_sales.line_total` - Column reference
- `SUM(fact_sales.line_total)` - Aggregation
- `fact_sales.quantity * fact_sales.unit_price` - Calculation
- `COUNT(DISTINCT dim_customer.customer_key)` - Distinct count

### Grain

The grain defines the level of detail for the metric:

- Empty `[]` - Total/aggregate level
- `[invoice_no]` - By invoice
- `[customer_key, product_key]` - By customer and product
- `[date]` - By date

### Format Types

| Format | Description | Example |
|--------|-------------|---------|
| `currency` | Monetary values | $1,234.56 |
| `number` | Plain numbers | 1,234 |
| `percentage` | Percentages | 12.34% |

### Example: Total Revenue

```yaml
metrics:
  total_revenue:
    name: "Total Revenue"
    expression: "SUM(fact_sales.line_total)"
    grain: []
    format: currency
    description: "Sum of all line totals in sales"
```

### Example: Average Order Value

```yaml
metrics:
  avg_order_value:
    name: "Average Order Value"
    expression: "AVG(order_total)"
    grain: [invoice_no]
    format: currency
    description: "Average revenue per invoice"
    dependencies:
      - order_total: "SUM(fact_sales.line_total) GROUP BY fact_sales.invoice_no"
```

### Example: Unique Customers

```yaml
metrics:
  unique_customers:
    name: "Unique Customers"
    expression: "COUNT(DISTINCT dim_customer.customer_key)"
    grain: []
    format: number
    description: "Number of unique customers"
```

### Example: Repeat Customer Rate

```yaml
metrics:
  repeat_rate:
    name: "Repeat Customer Rate"
    expression: "repeat_customers / total_customers"
    grain: []
    format: percentage
    description: "Percentage of customers with more than one order"
    dependencies:
      - total_customers: "COUNT(DISTINCT dim_customer.customer_key)"
      - repeat_customers: |
          SELECT COUNT(*) FROM (
            SELECT customer_key
            FROM fact_sales
            WHERE is_return = FALSE
            GROUP BY customer_key
            HAVING COUNT(*) > 1
          )
```

### Example: Revenue by Country

```yaml
metrics:
  revenue_by_country:
    name: "Revenue by Country"
    expression: "SUM(fact_sales.line_total)"
    grain: [dim_customer.country]
    format: currency
    description: "Total revenue grouped by customer country"
```

---

## Relationships

### What are Relationships?

Relationships define how concepts connect through foreign keys. The platform uses NetworkX to compute join paths automatically.

### Relationship Definition

Relationships are inferred from:

1. Foreign key definitions in concepts
2. Shared attribute names
3. Explicit relationship definitions

### Example: Join Path

```yaml
# From sale concept
attributes:
  - name: customer_key
    foreign_key: dim_customer.customer_key
  - name: product_key
    foreign_key: dim_product.product_key
  - name: date_key
    foreign_key: dim_date.date_key
```

This creates join paths:
- `fact_sales` → `dim_customer` (via customer_key)
- `fact_sales` → `dim_product` (via product_key)
- `fact_sales` → `dim_date` (via date_key)

### Complex Relationships

For many-to-many relationships, create bridge tables:

```yaml
concepts:
  order:
    table: fact_orders
    primary_key: order_key
    attributes:
      - name: order_key
        type: integer
      - name: customer_key
        type: integer
        foreign_key: dim_customer.customer_key

  order_item:
    table: fact_order_items
    primary_key: item_key
    attributes:
      - name: item_key
        type: integer
      - name: order_key
        type: integer
        foreign_key: fact_orders.order_key
      - name: product_key
        type: integer
        foreign_key: dim_product.product_key
```

---

## Best Practices

### 1. Concept Design

✅ **DO:**
- Use descriptive, consistent naming
- Include all relevant attributes
- Define clear primary keys
- Document foreign key relationships

❌ **DON'T:**
- Use ambiguous names (e.g., "data", "info")
- Omit important attributes
- Create circular foreign key relationships

### 2. Metric Design

✅ **DO:**
- Start with simple metrics
- Define clear grain
- Use meaningful names
- Document business logic

❌ **DON'T:**
- Create overly complex expressions
- Mix different grains in one metric
- Use ambiguous names

### 3. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Concepts | snake_case | `customer`, `product` |
| Tables | snake_case | `dim_customer`, `fact_sales` |
| Metrics | snake_case | `total_revenue`, `avg_order_value` |
| Attributes | snake_case | `customer_key`, `invoice_date` |

### 4. Performance Considerations

- Index foreign key columns
- Use appropriate grain for aggregations
- Consider materialized views for frequent queries
- Limit number of attributes per concept

### 5. Documentation

Always include:
- Clear descriptions
- Business context
- Data source information
- Update frequency

---

## Examples

### Complete Example: E-commerce Store

```yaml
# concepts/definitions.yaml
concepts:
  customer:
    table: dim_customer
    primary_key: customer_key
    display_name: "Customer"
    attributes:
      - name: customer_key
        type: integer
      - name: customer_id
        type: string
      - name: email
        type: string
      - name: first_name
        type: string
      - name: last_name
        type: string
      - name: country
        type: string
      - name: created_at
        type: datetime

  product:
    table: dim_product
    primary_key: product_key
    display_name: "Product"
    attributes:
      - name: product_key
        type: integer
      - name: sku
        type: string
      - name: name
        type: string
      - name: category
        type: string
      - name: brand
        type: string
      - name: price
        type: decimal

  order:
    table: fact_orders
    primary_key: order_key
    display_name: "Order"
    attributes:
      - name: order_key
        type: integer
      - name: order_id
        type: string
      - name: order_date
        type: datetime
      - name: customer_key
        type: integer
        foreign_key: dim_customer.customer_key
      - name: total_amount
        type: decimal

  order_item:
    table: fact_order_items
    primary_key: item_key
    display_name: "Order Item"
    attributes:
      - name: item_key
        type: integer
      - name: order_key
        type: integer
        foreign_key: fact_orders.order_key
      - name: product_key
        type: integer
        foreign_key: dim_product.product_key
      - name: quantity
        type: integer
      - name: unit_price
        type: decimal
      - name: line_total
        type: decimal
```

```yaml
# metrics/definitions.yaml
metrics:
  total_revenue:
    name: "Total Revenue"
    expression: "SUM(fact_order_items.line_total)"
    grain: []
    format: currency
    description: "Sum of all order item totals"

  total_orders:
    name: "Total Orders"
    expression: "COUNT(DISTINCT fact_orders.order_key)"
    grain: []
    format: number
    description: "Number of unique orders"

  avg_order_value:
    name: "Average Order Value"
    expression: "AVG(order_total)"
    grain: [fact_orders.order_key]
    format: currency
    description: "Average revenue per order"
    dependencies:
      - order_total: "SUM(fact_order_items.line_total) GROUP BY fact_orders.order_key"

  revenue_by_category:
    name: "Revenue by Category"
    expression: "SUM(fact_order_items.line_total)"
    grain: [dim_product.category]
    format: currency
    description: "Revenue grouped by product category"

  customer_lifetime_value:
    name: "Customer Lifetime Value"
    expression: "SUM(fact_order_items.line_total)"
    grain: [dim_customer.customer_key]
    format: currency
    description: "Total revenue per customer"
```

### Natural Language to SQL Translation

With the above definitions, the platform can translate:

| Question | Generated SQL |
|----------|---------------|
| "What was total revenue?" | `SELECT SUM(fact_order_items.line_total) FROM fact_order_items` |
| "Revenue by category?" | `SELECT dim_product.category, SUM(fact_order_items.line_total) FROM fact_order_items JOIN dim_product ON ... GROUP BY dim_product.category` |
| "Top 5 products by revenue?" | `SELECT dim_product.name, SUM(fact_order_items.line_total) FROM ... GROUP BY dim_product.name ORDER BY SUM(...) DESC LIMIT 5` |

---

## Validation

### Concept Validation

Check that concepts are properly defined:

```python
from retail_ontology.concepts import ConceptRegistry

registry = ConceptRegistry.from_yaml("concepts/definitions.yaml")

# Validate all concepts
for concept_name in registry.list():
    concept = registry.get(concept_name)
    print(f"Concept: {concept.display_name}")
    print(f"  Table: {concept.table}")
    print(f"  Primary Key: {concept.primary_key}")
    print(f"  Attributes: {len(concept.attributes)}")
```

### Metric Validation

Check that metrics are valid:

```python
from retail_ontology.metrics import MetricRegistry

registry = MetricRegistry.from_yaml("metrics/definitions.yaml")

# Validate all metrics
for metric_name in registry.list():
    metric = registry.get(metric_name)
    print(f"Metric: {metric.name}")
    print(f"  Expression: {metric.expression}")
    print(f"  Grain: {metric.grain}")
    print(f"  Format: {metric.format}")
```

### Query Validation

Validate queries against the ontology:

```python
from retail_ontology import OntologyEngine

engine = OntologyEngine.from_config("config.yaml")

# Validate a query
result = engine.ask("revenue by country")
if result.warnings:
    print("Warnings:", result.warnings)
```

---

## Extending the Ontology

### Adding New Concepts

1. Add to `concepts/definitions.yaml`
2. Update database schema if needed
3. Run migration

### Adding New Metrics

1. Add to `metrics/definitions.yaml`
2. Test with sample queries
3. Update documentation

### Adding New Attributes

1. Add to concept definition
2. Update database schema
3. Update ETL pipeline if needed

---

## Troubleshooting

### Common Issues

1. **Concept not found**
   - Check spelling in definitions
   - Verify YAML syntax
   - Reload configuration

2. **Metric computation error**
   - Check expression syntax
   - Verify table/column names
   - Check grain definition

3. **Join path not found**
   - Verify foreign key definitions
   - Check relationship consistency
   - Add explicit relationships if needed

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
retail ask "revenue by country"
