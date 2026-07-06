# Updated pyproject.toml Content

Copy this content to `pyproject.toml`:

```toml
[project]
name = "retail"
version = "0.1.0"
description = "AI Agent with Ontology-Augmented Generation (OAG) for Retail Analytics"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # Data Layer
    "duckdb>=1.0",
    "polars>=1.0",
    "sqlalchemy>=2.0",
    "ucimlrepo>=0.0.7",
    
    # Ontology Layer
    "pyyaml>=6.0",
    "networkx>=3.0",
    
    # Agent Layer
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "instructor>=1.0",
    "tenacity>=8.0",
    
    # LLM Providers
    "openai>=1.0",
    "anthropic>=0.30",
    "ollama>=0.3",
    
    # Interfaces
    "typer>=0.9",
    "rich>=13.0",
    "python-telegram-bot>=20.0",
    
    # Utilities
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "ruff>=0.3",
    "mypy>=1.0",
    "pre-commit>=3.0",
]
local-llm = [
    "llama-cpp-python>=0.2",
    "vllm>=0.5",
]
api = [
    "fastapi>=0.109",
    "uvicorn>=0.27",
]
all = [
    "retail[dev,local-llm,api]",
]

[project.scripts]
retail = "retail.__main__:main"
retail-download = "retail.deployment.scripts.download_data:main"
retail-build = "retail.deployment.scripts.build_warehouse:main"
retail-telegram = "retail.interfaces.telegram.bot:main"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "ruff>=0.3",
    "mypy>=1.0",
    "pre-commit>=3.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "T20", # flake8-print
]
ignore = [
    "E501",  # line too long (handled by formatter)
]
format.quote-style = "double"
format.indent-style = "space"

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "T201"]  # allow assert and print in tests

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
strict_optional = true
enable_error_code = ["unused-ignore"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--cov=retail",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.coverage.run]
source = ["src/retail"]
omit = ["tests/*", "*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"