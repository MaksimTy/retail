# Variant 2: Modular Service-Oriented Architecture

## Overview
Decompose the monolith into independent services communicating via well-defined APIs (gRPC for internal, REST for external). Each layer becomes a separately deployable service.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RETAIL AI AGENT (Service-Oriented)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │   CLI       │  │  Telegram   │  │  REST API   │  │   Web UI        │   │
│  │  (Client)   │  │  (Bot)      │  │  (Gateway)  │  │  (Frontend)     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │
│         │                │                │                   │            │
│         └────────────────┼────────────────┼───────────────────┘            │
│                          ▼                ▼                                │
│                 ┌─────────────────────────────────┐                        │
│                 │      API GATEWAY (Kong/Traefik) │                        │
│                 │  Auth │ Rate Limit │ Routing    │                        │
│                 └──────────────┬──────────────────┘                        │
│                                │                                           │
│         ┌──────────────────────┼──────────────────────┐                   │
│         ▼                      ▼                      ▼                   │
│ ┌───────────────┐    ┌─────────────────┐    ┌───────────────┐            │
│ │  AGENT SVC    │    │  ONTOLOGY SVC   │    │  DATA SVC     │            │
│ │  (Stateless)  │    │  (Stateful)     │    │  (Stateful)   │            │
│ │               │    │                 │    │               │            │
│ │ - Orchestrate │    │ - Concepts      │    │ - DuckDB/     │            │
│ │ - Tools       │    │ - Metrics       │    │   Postgres    │            │
│ │ - Conversation│    │ - Relationships │    │ - ETL Pipeline│            │
│ │ - LLM Factory │    │ - Query Builder │    │ - ucimlrepo   │            │
│ └───────┬───────┘    └────────┬────────┘    └───────┬───────┘            │
│         │                     │                     │                     │
│         │         ┌───────────┴───────────┐        │                     │
│         │         ▼                       ▼        │                     │
│         │  ┌─────────┐              ┌─────────┐     │                     │
│         │  │  LLM    │              │  CACHE  │     │                     │
│         │  │ PROXY   │              │ (Redis) │     │                     │
│         │  │(OpenRouter│             │         │     │                     │
│         │  │ + Local)│              └─────────┘     │                     │
│         │  └─────────┘                                │                     │
│         └─────────────────────────────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Service Contracts

### Data Service (gRPC)
```protobuf
service DataService {
  rpc ExecuteQuery(QueryRequest) returns (QueryResponse);
  rpc GetSchema(SchemaRequest) returns (SchemaResponse);
  rpc HealthCheck(HealthRequest) returns (HealthResponse);
}

message QueryRequest {
  string sql = 1;
  map<string, string> params = 2;
  int32 limit = 3;
}

message QueryResponse {
  repeated Row rows = 1;
  string[] columns = 2;
  int64 row_count = 3;
  int64 execution_ms = 4;
}
```

### Ontology Service (gRPC)
```protobuf
service OntologyService {
  rpc TranslateNLToQuery(NLRequest) returns (QueryPlan);
  rpc ValidateQuery(QueryPlan) returns (ValidationResult);
  rpc GetConcepts(ConceptRequest) returns (ConceptList);
  rpc GetMetrics(MetricRequest) returns (MetricList);
  rpc GetJoinPaths(JoinRequest) returns (JoinPathList);
}

message NLRequest {
  string question = 1;
  string locale = 2;
  ConversationContext context = 3;
}

message QueryPlan {
  string sql = 1;
  string[] tables_used = 2;
  string[] metrics_used = 3;
  Confidence confidence = 4;
  string explanation = 5;
}
```

### Agent Service (REST/gRPC)
```protobuf
service AgentService {
  rpc AskQuestion(AskRequest) returns (AskResponse);
  rpc StreamAnswer(StreamRequest) returns (stream StreamChunk);
  rpc GetHistory(HistoryRequest) returns (HistoryResponse);
  rpc ClearContext(ClearRequest) returns (ClearResponse);
}
```

## Characteristics

| Aspect | Description |
|--------|-------------|
| **Deployment** | Docker Compose / Kubernetes / separate containers |
| **State** | Data Service (DuckDB/Postgres), Ontology Service (Redis + config), Agent Service (stateless) |
| **Scaling** | Horizontal per service (Agent: stateless, easy; Data: read replicas) |
| **Latency** | Network hops (gRPC ~1-2ms, REST ~5-10ms) |
| **Development** | More complex, needs service contracts, integration testing |
| **Team** | Multiple teams can own different services |
| **Extensibility** | Swap any service independently (e.g., Data → Snowflake) |

## Technology Stack Additions
- **Service Framework**: grpcio, grpcio-tools, fastapi (for REST gateways)
- **Service Discovery**: Consul / etcd / Kubernetes DNS
- **API Gateway**: Kong / Traefik / NGINX
- **Observability**: OpenTelemetry, Prometheus, Grafana, Jaeger
- **Message Queue** (async): Redis Streams / RabbitMQ / Kafka
- **Config**: etcd / Consul / Spring Cloud Config equivalent

## Pros
- ✅ Independent scaling of components
- ✅ Technology diversity per service (Data in Rust/Go, Agent in Python)
- ✅ Fault isolation (LLM failure doesn't crash Data service)
- ✅ Team autonomy
- ✅ Production-ready for enterprise
- ✅ Can swap Data layer to Postgres/Snowflake/BigQuery
- ✅ Ontology service reusable across multiple agents

## Cons
- ❌ Significantly higher operational complexity
- ❌ Network latency between services
- ❌ Distributed system challenges (consistency, tracing, debugging)
- ❌ Overkill for pilot/PoC
- ❌ Requires DevOps maturity (K8s, service mesh, observability)
- ❌ Higher resource overhead (multiple containers, sidecars)

## Best For
- Production enterprise deployment
- Multiple teams working in parallel
- Need to integrate with existing data platform (Snowflake, etc.)
- High availability requirements
- Long-term product with dedicated platform team

---

## Implementation Plan for Variant 2

### Phase 1: Foundation & Service Contracts (Week 1-2)

#### Milestone 1.1: Monorepo Setup & Shared Infrastructure
- [ ] Create root `pyproject.toml` with uv workspace configuration
- [ ] Set up shared protobuf definitions (`proto/`)
- [ ] Create `Makefile` with service management commands
- [ ] Set up Docker Compose for local development
- [ ] Configure CI/CD pipeline (GitHub Actions)
- [ ] Set up pre-commit hooks (ruff, mypy, buf for protobuf)

#### Milestone 1.2: Service Contracts Definition
- [ ] Define `proto/data_service.proto` - Data Service gRPC contract
- [ ] Define `proto/ontology_service.proto` - Ontology Service gRPC contract
- [ ] Define `proto/agent_service.proto` - Agent Service gRPC contract
- [ ] Generate Python gRPC stubs with `grpcio-tools`
- [ ] Create shared Pydantic models for REST APIs
- [ ] Document API contracts in OpenAPI/Swagger

#### Milestone 1.3: Infrastructure Services
- [ ] Set up API Gateway (Traefik/Kong) with routing rules
- [ ] Configure service discovery (Consul/etcd or Kubernetes DNS)
- [ ] Set up Redis for caching and session storage
- [ ] Configure OpenTelemetry collector
- [ ] Set up Prometheus + Grafana for metrics
- [ ] Set up Jaeger for distributed tracing

---

### Phase 2: Data Service (Week 2-3)

#### Milestone 2.1: Data Service Core
- [ ] Create `services/data-service/pyproject.toml`
- [ ] Implement `DataService` gRPC server
- [ ] Implement DuckDB adapter with connection pooling
- [ ] Implement Postgres adapter (asyncpg)
- [ ] Add schema introspection endpoint
- [ ] Add health check endpoint

#### Milestone 2.2: ETL Pipeline
- [ ] Implement UCI downloader as separate job
- [ ] Create staging tables in DuckDB/Postgres
- [ ] Implement Kimball dimensional modeling ETL
- [ ] Add data quality checks and validation
- [ ] Create scheduled ETL jobs (Airflow/Prefect or cron)

#### Milestone 2.3: Data Service API
- [ ] Implement `ExecuteQuery` with parameter binding
- [ ] Implement `GetSchema` for table/column metadata
- [ ] Add query timeout and cancellation
- [ ] Add read replica support for scaling
- [ ] Implement connection pooling and retry logic

---

### Phase 3: Ontology Service (Week 3-4)

#### Milestone 3.1: Ontology Service Core
- [ ] Create `services/ontology-service/pyproject.toml`
- [ ] Implement `OntologyService` gRPC server
- [ ] Load concepts, metrics, relationships from YAML
- [ ] Build NetworkX relationship graph
- [ ] Implement join path resolution

#### Milestone 3.2: Query Engine
- [ ] Implement NL → LQP (Logical Query Plan) translator
- [ ] Add rule-based optimizer
- [ ] Implement LQP → Physical Plan (SQL) planner
- [ ] Add semantic validator against ontology
- [ ] Implement few-shot prompt management

#### Milestone 3.3: LLM Integration
- [ ] Implement LLM provider abstraction
- [ ] Add OpenRouter as first-class provider
- [ ] Add Ollama, OpenAI, Anthropic providers
- [ ] Implement structured output with instructor
- [ ] Add model routing (cheap/balanced/premium tiers)
- [ ] Implement fallback chain

---

### Phase 4: Agent Service (Week 4-5)

#### Milestone 4.1: Agent Service Core
- [ ] Create `services/agent-service/pyproject.toml`
- [ ] Implement `AgentService` gRPC/REST server
- [ ] Implement conversation context management (Redis)
- [ ] Implement orchestration logic (NL → Ontology → Data → Answer)
- [ ] Add streaming response support

#### Milestone 4.2: Agent Features
- [ ] Implement clarification handling for ambiguous questions
- [ ] Add conversation history and context
- [ ] Implement function calling tools
- [ ] Add answer formatting and explanation generation
- [ ] Implement rate limiting and quota management

---

### Phase 5: Interface Services (Week 5-6)

#### Milestone 5.1: CLI Client
- [ ] Create `services/cli-client/pyproject.toml`
- [ ] Implement Typer-based CLI
- [ ] Add gRPC client for Agent Service
- [ ] Implement Rich formatting for output
- [ ] Add interactive REPL mode

#### Milestone 5.2: Telegram Bot
- [ ] Create `services/telegram-bot/pyproject.toml`
- [ ] Implement python-telegram-bot v20 application
- [ ] Add command handlers (/start, /help, /ask)
- [ ] Implement inline query support
- [ ] Add user authorization and session management
- [ ] Connect to Agent Service via gRPC

#### Milestone 5.3: REST API Gateway
- [ ] Create `services/api-gateway/pyproject.toml`
- [ ] Implement FastAPI application
- [ ] Add REST endpoints proxying to Agent Service
- [ ] Implement authentication (API keys/JWT)
- [ ] Add rate limiting
- [ ] Generate OpenAPI documentation

#### Milestone 5.4: Web UI (Optional)
- [ ] Create `services/web-ui/` (React/Streamlit)
- [ ] Implement chat interface
- [ ] Add conversation history
- [ ] Add visualization components

---

### Phase 6: Observability & Production Hardening (Week 6-8)

#### Milestone 6.1: Observability
- [ ] Add structured logging with correlation IDs
- [ ] Implement distributed tracing (OpenTelemetry → Jaeger)
- [ ] Add Prometheus metrics (latency, errors, token usage)
- [ ] Create Grafana dashboards
- [ ] Set up alerting rules

#### Milestone 6.2: Security & Reliability
- [ ] Implement mTLS between services
- [ ] Add API authentication and authorization
- [ ] Implement circuit breakers (resilience4j/pybreaker)
- [ ] Add request/response validation
- [ ] Implement graceful degradation

#### Milestone 6.3: Deployment & Operations
- [ ] Create Kubernetes manifests (Deployment, Service, Ingress)
- [ ] Configure Horizontal Pod Autoscaler
- [ ] Set up secrets management (Vault/Sealed Secrets)
- [ ] Create runbooks for common operations
- [ ] Implement backup/restore for data service
- [ ] Load testing and capacity planning

---

### Detailed Task Breakdown by Week

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Monorepo + Protobuf + Infrastructure | Working Docker Compose, gRPC stubs, API Gateway |
| 2 | Data Service + ETL | Data Service gRPC, DuckDB/Postgres, ETL pipeline |
| 3 | Ontology Service + Query Engine | Ontology Service gRPC, NL→SQL, LLM providers |
| 4 | Agent Service | Agent Service gRPC/REST, conversation management |
| 5 | Interface Services | CLI, Telegram Bot, REST API Gateway |
| 6 | Observability + Security | Tracing, metrics, logging, mTLS, circuit breakers |
| 7 | Kubernetes Deployment | K8s manifests, HPA, secrets, CI/CD |
| 8 | Testing + Hardening | Integration tests, load tests, runbooks |

---

### Service Repository Structure

```
retail/
├── pyproject.toml              # Root workspace config
├── proto/                      # Shared protobuf definitions
│   ├── data_service.proto
│   ├── ontology_service.proto
│   ├── agent_service.proto
│   └── common.proto
├── docker-compose.yml          # Local development
├── Makefile
├── services/
│   ├── data-service/
│   │   ├── pyproject.toml
│   │   ├── src/data_service/
│   │   │   ├── server.py
│   │   │   ├── adapters/
│   │   │   │   ├── duckdb.py
│   │   │   │   └── postgres.py
│   │   │   ├── etl/
│   │   │   │   ├── downloader.py
│   │   │   │   ├── cleaner.py
│   │   │   │   └── loader.py
│   │   │   └── health.py
│   │   └── tests/
│   ├── ontology-service/
│   │   ├── pyproject.toml
│   │   ├── src/ontology_service/
│   │   │   ├── server.py
│   │   │   ├── concepts/
│   │   │   ├── metrics/
│   │   │   ├── relationships/
│   │   │   ├── query_engine/
│   │   │   │   ├── translator.py
│   │   │   │   ├── optimizer.py
│   │   │   │   ├── planner.py
│   │   │   │   └── validator.py
│   │   │   │   │   └── llm/
│   │   │       ├── base.py
│   │   │       ├── openrouter.py
│   │   │       ├── ollama.py
│   │   │       └── factory.py
│   │   └── tests/
│   ├── agent-service/
│   │   ├── pyproject.toml
│   │   ├── src/agent_service/
│   │   │   ├── server.py
│   │   │   ├── core.py
│   │   │   ├── conversation.py
│   │   │   └── tools.py
│   │   └── tests/
│   ├── cli-client/
│   │   ├── pyproject.toml
│   │   └── src/cli_client/
│   ├── telegram-bot/
│   │   ├── pyproject.toml
│   │   └── src/telegram_bot/
│   ├── api-gateway/
│   │   ├── pyproject.toml
│   │   └── src/api_gateway/
│   └── web-ui/                 # Optional
├── k8s/                        # Kubernetes manifests
│   ├── base/
│   ├── overlays/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── helm/
└── docs/
    ├── architecture.md
    ├── api.md
    ├── deployment.md
    └── operations.md
```

---

### Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Distributed system complexity | High | High | Start with Docker Compose, invest in observability early |
| gRPC versioning | Medium | Medium | Use protobuf with backward compatibility rules |
| Network latency | Medium | Medium | Co-locate services, use connection pooling, caching |
| Data consistency | Medium | High | Eventual consistency patterns, saga for distributed transactions |
| Operational burden | High | High | Invest in automation, runbooks, GitOps |
| Team coordination | Medium | Medium | Clear service contracts, API-first development |

---

### Success Criteria

- [ ] All services deploy independently via Docker Compose
- [ ] gRPC health checks pass for all services
- [ ] End-to-end query: CLI → API Gateway → Agent → Ontology → Data → Answer
- [ ] Telegram bot responds to `/ask` commands
- [ ] REST API returns JSON answers with OpenAPI docs
- [ ] Distributed tracing shows full request flow
- [ ] Horizontal scaling works (add Agent Service replicas)
- [ ] Kubernetes deployment succeeds in dev cluster
- [ ] Load test: 100 req/s, <500ms p99 latency
- [ ] Failover test: kill Data Service, system degrades gracefully

---

### Next Immediate Steps

1. **Create monorepo structure** with `proto/` directory
2. **Define protobuf contracts** for all three services
3. **Set up Docker Compose** with API Gateway, Redis, services
4. **Generate gRPC stubs** and create shared Python package
5. **Implement Data Service** with DuckDB adapter first
6. **Build first ETL pipeline** to populate warehouse
7. **Wire up Ontology Service** with basic concepts/metrics
8. **First end-to-end test** across all services