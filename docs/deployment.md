# Retail AI Agent Deployment Guide

## Overview

This document describes how to deploy the Retail AI Agent in various environments.

## Local Development

### Prerequisites
- Python 3.13+
- Ollama (optional, for local LLM)
- uv package manager

### Setup
```bash
# Clone the repository
git clone <repo-url>
cd retail

# Install dependencies
uv pip install -e .

# Download and process data
python scripts/download_data.py
python scripts/build_warehouse.py

# Run the CLI
retail ask "What is the total revenue?"
```

## Docker Deployment

### Build the Image
```bash
docker build -t retail-agent .
```

### Run the Container
```bash
docker run -p 8000:8000 \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  retail-agent
```

### Docker Compose
```yaml
version: '3.8'
services:
  retail-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./data:/app/data
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama

volumes:
  ollama:
```

## Production Deployment

### Recommended Architecture
- **Reverse Proxy**: Nginx or Traefik
- **Container Orchestration**: Kubernetes or Docker Swarm
- **Database**: DuckDB file stored on persistent volume
- **LLM**: Ollama running on dedicated GPU instance

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| LLM_PROVIDER | LLM provider (ollama, openai, anthropic) | ollama |
| OLLAMA_BASE_URL | Ollama server URL | http://localhost:11434 |
| OLLAMA_MODEL | Ollama model name | llama3.2 |
| OPENAI_API_KEY | OpenAI API key | - |
| OPENAI_MODEL | OpenAI model name | gpt-4o |
| DUCKDB_DATABASE_PATH | Path to DuckDB database | ./data/warehouse/retail.duckdb |
| API_HOST | API server host | 0.0.0.0 |
| API_PORT | API server port | 8000 |

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
docker logs retail-agent