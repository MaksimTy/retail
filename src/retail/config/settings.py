"""
Application settings using Pydantic BaseSettings.
"""

from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    DATA_SOURCE_PATH: Path = PROJECT_ROOT / "data" / "source"
    DATA_STAGING_PATH: Path = PROJECT_ROOT / "data" / "staging"
    DATA_WAREHOUSE_PATH: Path = PROJECT_ROOT / "data" / "warehouse"
    
    # LLM Configuration
    LLM_PROVIDER: str = Field(default="ollama", env="LLM_PROVIDER")  # openai, anthropic, ollama, llamacpp
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str | None = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str | None = Field(default=None, env="TELEGRAM_CHAT_ID")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()