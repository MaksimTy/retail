# API Documentation

## Retail Ontology Platform - Core Library API

### Installation

```bash
# From monorepo root
uv sync --all-extras

# Or install directly
pip install retail-ontology
pip install retail-ontology[postgres]  # with PostgreSQL adapter
pip install retail-ontology[snowflake]  # with Snowflake adapter
pip install retail-ontology[all]  # all adapters
```

### Quick Start

```python
from retail_ontology import OntologyEngine, QueryResult

# Initialize engine with config
engine = OntologyEngine.from_config("config.yaml")

# Ask a question
result: QueryResult = engine.ask("What was total revenue from UK in Dec 2011?")
print(result.answer)      # "£1,234,567.89"
print(result.sql)         # "SELECT SUM(line_total) FROM fact_sales..."
print(result.explanation) # "Joined fact_sales → dim_customer, filtered..."

# Advanced usage with conversation
session = engine.create_session()
session.ask("Top 5 products by revenue")
session.ask("And for UK only?")  # Context-aware
```

### Core API Reference

#### OntologyEngine

Main entry point for the ontology platform.

```python
class OntologyEngine:
    @classmethod
    def from_config(cls, config_path: str | Path) -> "OntologyEngine":
        """Create engine from configuration file."""

    def ask(self, question: str) -> QueryResult:
        """Ask a natural language question."""

    def create_session(self) -> Session:
        """Create a conversation session."""

    def translate(self, question: str, context: dict | None = None) -> LogicalQueryPlan:
        """Translate NL question to Logical Query Plan."""

    def validate(self, lqp: LogicalQueryPlan) -> ValidationResult:
        """Validate LQP against ontology."""

    def plan(self, lqp: LogicalQueryPlan) -> str:
        """Generate SQL from LQP."""

    def execute(self, sql: str) -> list[dict]:
        """Execute SQL query."""

    def format_answer(self, lqp: LogicalQueryPlan, data: list[dict]) -> str:
        """Format query results as natural language answer."""
```

#### QueryResult

Result object returned from `ask()`.

```python
@dataclass
class QueryResult:
    answer: str | None = None
    sql: str | None = None
    lqp: LogicalQueryPlan | None = None
    data: list[dict] | None = None
    error: str | None = None
    warnings: list[str] | None = None
    execution_time_ms: float | None = None
    token_usage: dict | None = None
```

#### Session

Conversation session for context-aware queries.

```python
class Session:
    def ask(self, question: str) -> QueryResult:
        """Ask a question with conversation context."""

    def get_context(self) -> dict:
        """Get conversation context."""

    def clear(self) -> None:
        """Clear conversation history."""
```

### Configuration

Create a `config.yaml` or use environment variables:

```yaml
llm:
  provider: openrouter
  model: anthropic/claude-3.5-sonnet
  api_key: ${OPENROUTER_API_KEY}
  temperature: 0.1
  max_tokens: 4096

database:
  adapter: duckdb
  duckdb_path: ./data/warehouse.duckdb
  postgres_dsn: postgresql://user:password@localhost:5432/retail_ontology

concepts:
  - name: Customer
    table: dim_customer
    primary_key: customer_key
    attributes:
      - name: customer_key
        type: integer
      - name: country
        type: string

metrics:
  - name: Revenue
    expression: sum(fact_sales.line_total)
    grain: day
    format: currency
```

### Concepts API

#### ConceptRegistry

```python
from retail_ontology.concepts import ConceptRegistry, Concept

# Load from YAML
registry = ConceptRegistry.from_yaml("concepts/definitions.yaml")

# Get concept by name
customer = registry.get("customer")

# List all concepts
all_concepts = registry.list()

# Get concept attributes
attributes = customer.attributes

# Get primary key
pk = customer.primary_key

# Get foreign keys
fks = customer.foreign_keys
```

#### Concept Definition

```yaml
concepts:
  customer:
    table: dim_customer
    primary_key: customer_key
    display_name: "Customer"
    attributes:
      - name: customer_key
        type: integer
        description: "Surrogate key"
      - name: customer_id
        type: string
        description: "Original customer ID from source"
      - name: country
        type: string
        description: "Customer country"
```

### Metrics API

#### MetricRegistry

```python
from retail_ontology.metrics import MetricRegistry

# Load from YAML
registry = MetricRegistry.from_yaml("metrics/definitions.yaml")

# Get metric by name
revenue = registry.get("total_revenue")

# Compute metric
result = registry.compute("total_revenue", filters={"country": "UK"})

# List all metrics
all_metrics = registry.list()
```

#### Metric Definition

```yaml
metrics:
  total_revenue:
    name: "Total Revenue"
    expression: "SUM(fact_sales.line_total)"
    grain: [customer_key, product_key, invoice_date]
    format: "currency"
    description: "Sum of all line totals"

  avg_order_value:
    name: "Average Order Value"
    expression: "AVG(order_total)"
    grain: [invoice_no]
    format: "currency"
    description: "Average revenue per invoice"
    dependencies:
      - order_total: "SUM(fact_sales.line_total) GROUP BY invoice_no"
```

### Data Adapters API

#### DataAdapter Protocol

```python
from retail_ontology.adapters import DataAdapter

class DataAdapter(Protocol):
    async def connect(self) -> None:
        """Establish connection."""

    async def disconnect(self) -> None:
        """Close connection."""

    async def execute(self, sql: str, params: dict | None = None) -> QueryResult:
        """Execute SQL query."""

    async def execute_many(self, sql: str, params_list: list[dict]) -> None:
        """Execute multiple queries."""

    async def fetch_schema(self) -> SchemaInfo:
        """Get database schema."""

    async def health_check(self) -> bool:
        """Check connection health."""
```

#### DuckDB Adapter

```python
from retail_ontology.adapters import DuckDBAdapter

adapter = DuckDBAdapter(path="./data/warehouse.duckdb")
await adapter.connect()
result = await adapter.execute("SELECT * FROM dim_customer LIMIT 10")
await adapter.disconnect()
```

#### PostgreSQL Adapter

```python
from retail_ontology.adapters import PostgresAdapter

adapter = PostgresAdapter(dsn="postgresql://user:pass@localhost:5432/db")
await adapter.connect()
result = await adapter.execute("SELECT * FROM dim_customer LIMIT 10")
await adapter.disconnect()
```

### LLM Providers API

#### LLMProvider Protocol

```python
from retail_ontology.llm import LLMProvider
from pydantic import BaseModel

class LLMProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        """Get text completion."""

    async def complete_structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        """Get structured completion."""

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
```

#### OpenRouter Provider

```python
from retail_ontology.llm import OpenRouterProvider

provider = OpenRouterProvider(
    api_key="your-api-key",
    model="openai/gpt-4o-mini"
)

# Text completion
response = await provider.complete("Translate to SQL: revenue by country")

# Structured completion
from pydantic import BaseModel

class QueryPlan(BaseModel):
    metrics: list[str]
    dimensions: list[str]
    filters: list[dict]

plan = await provider.complete_structured(prompt, QueryPlan)
```

#### Provider Factory

```python
from retail_ontology.llm import LLMFactory

# Create provider from config
provider = LLMFactory.create(
    provider="openrouter",
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"
)
```

### Query Engine API

#### LogicalQueryPlan (LQP)

```python
from retail_ontology.query_engine import LogicalQueryPlan, MetricRef, DimensionRef

lqp = LogicalQueryPlan(
    metrics=[MetricRef(name="total_revenue")],
    dimensions=[DimensionRef(concept="customer", attribute="country")],
    filters=[],
    grain=[],
    order_by=None,
    limit=None,
    confidence=0.95,
    explanation="Aggregated revenue by customer country",
    warnings=[]
)
```

#### Translator

```python
from retail_ontology.query_engine import Translator

translator = Translator(ontology_engine)
lqp = await translator.translate("What was total revenue by country?")
```

#### Optimizer

```python
from retail_ontology.query_engine import Optimizer

optimizer = Optimizer()
optimized_lqp = optimizer.optimize(lqp)
```

#### Planner

```python
from retail_ontology.query_engine import Planner

planner = Planner()
sql = planner.plan(lqp)
```

### CLI API

The CLI provides a command-line interface to the library:

```bash
# Ask a question
retail ask "revenue by country"

# Build warehouse
retail build

# Download data
retail download

# Show configuration
retail config show

# List concepts
retail models concepts

# List metrics
retail models metrics
```

### REST API Endpoints

The REST API wrapper provides HTTP endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask a natural language question |
| `/ask/stream` | POST | Streaming answer (SSE) |
| `/health` | GET | Health check |
| `/concepts` | GET | List all concepts |
| `/metrics` | GET | List all metrics |
| `/schema` | GET | Database schema introspection |

#### Ask a Question (Sync)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"question": "revenue by country", "session_id": "optional"}'
```

#### Ask a Question (Stream)

```bash
curl -X POST http://localhost:8000/ask/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"question": "revenue by country"}'
```

### Error Handling

```python
from retail_ontology import OntologyEngine, QueryResult

engine = OntologyEngine.from_config("config.yaml")
result = engine.ask("invalid question")

if result.error:
    print(f"Error: {result.error}")
    # Handle error appropriately
```

### Logging

The library uses loguru for structured logging:

```python
from loguru import logger

# Configure logging
logger.remove()
logger.add("app.log", format="{time} {level} {message}", level="INFO")

# Or use JSON format
logger.add(sys.stderr, format="{message}", level="INFO")
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `DUCKDB_PATH` | Path to DuckDB warehouse | `./data/warehouse.duckdb` |
| `POSTGRES_DSN` | PostgreSQL connection string | - |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider | `openrouter` |
| `DEFAULT_LLM_MODEL` | Default LLM model | `anthropic/claude-3.5-sonnet` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (json/text) | `json` |
