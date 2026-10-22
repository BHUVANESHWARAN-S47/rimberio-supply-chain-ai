import os
from typing import Optional
from pydantic import BaseModel, Field

class Settings(BaseModel):
    PROJECT_NAME: str = "RIMBERIO Enterprise Multi-Agent Supply Chain Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'rimberio_enterprise.db'))}"
        )
    )
    
    # LLM Settings (local Ollama is the default; Groq remains optional)
    LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "ollama"))
    OLLAMA_BASE_URL: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    OLLAMA_MODEL: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2:3b"))
    GROQ_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    OPENAI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    DEFAULT_LLM_MODEL: str = Field(default_factory=lambda: os.getenv("DEFAULT_LLM_MODEL", "llama3.2:3b"))
    FALLBACK_LLM_MODEL: str = "llama-3.1-8b-instant"
    LLM_TEMPERATURE: float = 0.1
    
    # Observability
    LOG_LEVEL: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    LOG_DIR: str = Field(
        default_factory=lambda: os.getenv(
            "LOG_DIR",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "logs"))
        )
    )

settings = Settings()
