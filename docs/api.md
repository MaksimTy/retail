# Retail AI Agent API Documentation

## Overview

The Retail AI Agent provides a REST API for programmatic access to the OAG-powered retail analytics.

## Endpoints

### POST /ask

Ask a natural language question about the retail data.

**Request Body:**
```json
{
  "question": "What is the total revenue?"
}
```

**Response:**
```json
{
  "question": "What is the total revenue?",
  "sql": "SELECT SUM(line_total) AS total_revenue FROM fact_sales;",
  "answer": "The answer to 'What is the total revenue?' is: $1,234,567.89"
}
```

### GET /metrics

Get available metrics.

**Response:**
```json
{
  "metrics": [
    "total_revenue",
    "order_count",
    "average_order_value",
    "customer_count",
    "product_count"
  ]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "database": "connected"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid question format"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to process question"
}