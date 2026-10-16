import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeLens"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretkey_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen2.5:7b"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    
    EMBEDDING_PROVIDER: str = "sentence_transformers"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_WEBHOOK_SECRET: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
