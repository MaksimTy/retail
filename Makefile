# Retail Ontology Platform - Makefile
# Common development tasks

.PHONY: help install sync test lint format typecheck clean build publish docs

# Default target
help:
	@echo "Retail Ontology Platform - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install all dependencies (uv sync)"
	@echo "  make sync         - Sync dependencies (uv sync)"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make typecheck    - Run mypy type checking"
	@echo "  make check        - Run all checks (lint, format, typecheck, test)"
	@echo ""
	@echo "Building:"
	@echo "  make build        - Build all packages"
	@echo "  make build-ontology - Build retail-ontology package"
	@echo "  make build-cli    - Build retail-cli package"
	@echo "  make build-telegram - Build retail-telegram package"
	@echo "  make build-api    - Build retail-api package"
	@echo ""
	@echo "Publishing:"
	@echo "  make publish      - Publish all packages to PyPI"
	@echo "  make publish-test - Publish all packages to TestPyPI"
	@echo ""
	@echo "Data:"
	@echo "  make download     - Download UCI dataset"
	@echo "  make build-warehouse - Build DuckDB warehouse"
	@echo ""
	@echo "Running:"
	@echo "  make run-cli      - Run CLI (retail ask '...')"
	@echo "  make run-api      - Run FastAPI server"
	@echo "  make run-telegram - Run Telegram bot"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start docker-compose"
	@echo "  make docker-down  - Stop docker-compose"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make clean-all    - Clean everything including .venv"

# Setup
install:
	uv sync --all-extras

sync:
	uv sync

# Testing
test:
	uv run pytest -v

test-unit:
	uv run pytest -v -m "not integration"

test-integration:
	uv run pytest -v -m "integration"

test-cov:
	uv run pytest --cov=packages/retail-ontology/src --cov=packages/retail-cli/src --cov=packages/retail-telegram/src --cov=packages/retail-api/src --cov-report=html --cov-report=term

# Linting & Formatting
lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy packages/retail-ontology/src packages/retail-cli/src packages/retail-telegram/src packages/retail-api/src

check: lint format-check typecheck test

# Building
build: build-ontology build-cli build-telegram build-api

build-ontology:
	cd packages/retail-ontology && uv build

build-cli:
	cd packages/retail-cli && uv build

build-telegram:
	cd packages/retail-telegram && uv build

build-api:
	cd packages/retail-api && uv build

# Publishing
publish: build
	uv publish packages/retail-ontology/dist/*
	uv publish packages/retail-cli/dist/*
	uv publish packages/retail-telegram/dist/*
	uv publish packages/retail-api/dist/*

publish-test: build
	uv publish --publish-url https://test.pypi.org/legacy/ packages/retail-ontology/dist/*
	uv publish --publish-url https://test.pypi.org/legacy/ packages/retail-cli/dist/*
	uv publish --publish-url https://test.pypi.org/legacy/ packages/retail-telegram/dist/*
	uv publish --publish-url https://test.pypi.org/legacy/ packages/retail-api/dist/*

# Data
download:
	uv run python -m retail_ontology.scripts.download_data

build-warehouse:
	uv run python -m retail_ontology.scripts.build_warehouse

# Running
run-cli:
	uv run retail

run-api:
	uv run uvicorn retail_api.main:app --host 0.0.0.0 --port 8000 --reload

run-telegram:
	uv run python -m retail_telegram.main

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	rm -rf .venv
	rm -rf .uv
	rm -rf packages/*/.venv
