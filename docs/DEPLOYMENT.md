# Deployment Guide

## Retail Ontology Platform - Deployment Guide

This document provides comprehensive deployment instructions for the Retail Ontology Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Serverless Deployment](#serverless-deployment)
6. [Production Considerations](#production-considerations)
7. [Monitoring & Observability](#monitoring--observability)

---

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB for codebase, additional for data warehouse

### Required Services

- **OpenRouter API Key** (or other LLM provider)
- **Database**: DuckDB (local), PostgreSQL, or Snowflake

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/retail-ontology-platform.git
cd retail-ontology-platform
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv sync --all-extras

# Or using pip
pip install -e .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 4. Download and Build Data

```bash
# Download UCI Online Retail dataset
make download

# Build DuckDB warehouse
make build-warehouse
```

### 5. Run the Application

```bash
# Run CLI
make run-cli

# Run API server
make run-api

# Run Telegram bot
make run-telegram
```

---

## Docker Deployment

### 1. Build Docker Images

```bash
# Build all images
make docker-build

# Or build individual images
docker build -t retail-ontology:latest -f packages/retail-ontology/Dockerfile .
docker build -t retail-cli:latest -f packages/retail-cli/Dockerfile .
docker build -t retail-api:latest -f packages/retail-api/Dockerfile .
docker build -t retail-telegram:latest -f packages/retail-telegram/Dockerfile .
```

### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ontology-api:
    image: retail-api:latest
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DUCKDB_PATH=/data/warehouse.duckdb
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./data:/data
    depends_on:
      - ontology-db

  ontology-db:
    image: duckdb:latest
    volumes:
      - ./data:/data
    ports:
      - "8011:8011"

  ontology-cli:
    image: retail-cli:latest
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DUCKDB_PATH=/data/warehouse.duckdb
    volumes:
      - ./data:/data
    command: ["retail", "ask", "revenue by country"]

  ontology-telegram:
    image: retail-telegram:latest
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DUCKDB_PATH=/data/warehouse.duckdb
    volumes:
      - ./data:/data
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Initialize Data

```bash
# Download data
docker-compose exec ontology-cli retail download

# Build warehouse
docker-compose exec ontology-cli retail build
```

---

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

Create `k8s/ontology-api.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ontology-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ontology-api
  template:
    metadata:
      labels:
        app: ontology-api
    spec:
      containers:
      - name: api
        image: retail-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: ontology-secrets
              key: openrouter-api-key
        - name: DUCKDB_PATH
          value: /data/warehouse.duckdb
        volumeMounts:
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ontology-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: ontology-api
spec:
  selector:
    app: ontology-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: Secret
metadata:
  name: ontology-secrets
type: Opaque
data:
  openrouter-api-key: <base64-encoded-api-key>
```

### 2. Apply Manifests

```bash
kubectl apply -f k8s/
```

### 3. Scale Deployment

```bash
kubectl scale deployment ontology-api --replicas=5
```

### 4. Check Status

```bash
kubectl get pods
kubectl logs -l app=ontology-api
kubectl describe service ontology-api
```

---

## Serverless Deployment

### AWS Lambda

#### 1. Create Lambda Function

```python
# lambda_handler.py
import json
from retail_ontology import OntologyEngine

engine = OntologyEngine.from_config("config.yaml")

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    question = body.get('question', '')

    result = engine.ask(question)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'answer': result.answer,
            'sql': result.sql,
            'execution_time_ms': result.execution_time_ms
        })
    }
```

#### 2. Package and Deploy

```bash
# Create deployment package
zip -r lambda-deployment.zip .

# Deploy via AWS CLI
aws lambda create-function \
  --function-name retail-ontology-api \
  --runtime python3.11 \
  --role arn:aws:iam::account:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda-deployment.zip
```

### Google Cloud Functions

```bash
# Deploy
gcloud functions deploy retail-ontology-ask \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point lambda_handler
```

### Azure Functions

```bash
# Deploy
func azure functionapp publish retail-ontology-func
```

---

## Production Considerations

### 1. Database Selection

| Database | Use Case | Pros | Cons |
|----------|----------|------|------|
| DuckDB | Development, Single-node | Zero config, fast | Not distributed |
| PostgreSQL | Production | ACID, scalable | Requires setup |
| Snowflake | Enterprise | Serverless, scalable | Cost, complexity |

### 2. LLM Provider Selection

| Provider | Use Case | Cost | Latency |
|----------|----------|------|---------|
| OpenRouter | Multi-model | Low | Medium |
| OpenAI | High quality | Medium | Low |
| Anthropic | Safety | Medium | Medium |
| Ollama | Local | Free | High |

### 3. Environment Configuration

Production `.env` example:

```bash
# LLM Configuration
OPENROUTER_API_KEY=your-production-api-key
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=openai/gpt-4o-mini

# Database
DUCKDB_PATH=/data/warehouse.duckdb
POSTGRES_DSN=postgresql://user:password@postgres:5432/retail

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
API_KEY=your-secure-api-key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Observability
PROMETHEUS_PORT=9090
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

### 4. Secrets Management

Use environment variables or secret managers:

```bash
# Kubernetes Secrets
kubectl create secret generic ontology-secrets \
  --from-literal=openrouter-api-key=your-key \
  --from-literal=postgres-password=your-password

# Docker Secrets
echo "your-api-key" | docker secret create openrouter_api_key -
```

---

## Monitoring & Observability

### 1. Health Checks

```bash
# API Health Check
curl http://localhost:8000/health

# Database Health Check
uv run python -c "
from retail_ontology.adapters import DuckDBAdapter
import asyncio

async def check():
    adapter = DuckDBAdapter('./data/warehouse.duckdb')
    await adapter.connect()
    print(await adapter.health_check())
    await adapter.disconnect()

asyncio.run(check())
"
```

### 2. Prometheus Metrics

Enable metrics endpoint:

```python
# metrics.py
from prometheus_client import Counter, Histogram, start_http_server

QUERY_COUNT = Counter('ontology_queries_total', 'Total queries')
QUERY_DURATION = Histogram('ontology_query_duration_seconds', 'Query duration')

# In your API routes
@router.post("/ask")
async def ask(question: str):
    start = time.time()
    result = engine.ask(question)
    QUERY_COUNT.inc()
    QUERY_DURATION.observe(time.time() - start)
    return result
```

### 3. OpenTelemetry Tracing

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("ask")
def ask(question: str):
    with tracer.start_as_current_span("translate"):
        lqp = translator.translate(question)
    with tracer.start_as_current_span("execute"):
        result = adapter.execute(sql)
    return result
```

### 4. Logging Configuration

```python
# Structured JSON logging
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format='{"time": "{time}", "level": "{level}", "message": "{message}", "module": "{module}"}',
    level="INFO"
)
```

### 5. Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Sync dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest

      - name: Build packages
        run: make build

      - name: Publish to PyPI
        run: make publish
        env:
          API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

---

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify `OPENROUTER_API_KEY` is set correctly
   - Check API key has not expired

2. **Database Connection Issues**
   - Verify database path/credentials
   - Check firewall rules for remote databases

3. **Memory Issues**
   - Increase container memory limits
   - Consider PostgreSQL for large datasets

4. **Slow Queries**
   - Check DuckDB indexes
   - Consider materialized views for frequent queries

### Logs Location

```bash
# CLI logs
uv run retail ask "question" 2>&1 | tee cli.log

# API logs
docker logs ontology-api
kubectl logs -l app=ontology-api

# Telegram logs
uv run python -m retail_telegram.main 2>&1 | tee telegram.log
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale API replicas
kubectl scale deployment ontology-api --replicas=10

# Load balancer configuration
# Use Kubernetes Service with type LoadBalancer
# or Ingress controller for advanced routing
```

### Vertical Scaling

```bash
# Increase resource limits
kubectl patch deployment ontology-api -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"requests":{"memory":"1Gi","cpu":"500m"},"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'
```

### Database Scaling

For PostgreSQL:
- Use connection pooling (pgbouncer)
- Read replicas for read-heavy workloads
- Partitioning for large tables

---

## Security

### 1. API Authentication

```python
# auth.py
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials
```

### 2. Rate Limiting

```python
# rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/ask")
@limiter.limit("10/minute")
async def ask(request: Request, question: str):
    ...
```

### 3. TLS/SSL

```bash
# Using Caddy
caddy run --config Caddyfile

# Caddyfile
retail-api.example.com {
    reverse_proxy localhost:8000
    tls you@example.com
}
```

---

## Backup & Recovery

### 1. DuckDB Backup

```bash
# Backup
cp data/warehouse.duckdb backups/warehouse-$(date +%Y%m%d).duckdb

# Restore
cp backups/warehouse-20240101.duckdb data/warehouse.duckdb
```

### 2. PostgreSQL Backup

```bash
# Logical backup
pg_dump -U user -h localhost retail_ontology > backup.sql

# Physical backup
pg_basebackup -D /var/lib/postgresql/backup -U replicator
```

### 3. Data Pipeline Recovery

```bash
# Re-run ETL pipeline
retail download
retail build
