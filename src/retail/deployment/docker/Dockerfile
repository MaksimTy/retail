FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
RUN uv pip install -e .

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LLM_PROVIDER=ollama
ENV OLLAMA_BASE_URL=http://ollama:11434

# Expose port
EXPOSE 8000

# Run the agent
CMD ["python", "-m", "src.retail"]