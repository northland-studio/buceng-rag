from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.3
    LLM_TIMEOUT: int = 60
    LLM_THINKING_ENABLED: bool = True
    LLM_REASONING_EFFORT: str = "high"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    MAX_RETRIEVAL_RESULTS: int = 10
    HISTORY_COLLECTION: str = "history_records"
    MAX_HISTORY_RESULTS: int = 5
    HF_MIRROR: Optional[str] = None
    CORS_ORIGINS: str = "*"
    COLLECTION_NAME: str = "sociology_cards"
    GOLDEN_SAMPLES_COLLECTION: str = "golden_samples"
    SEED_CARDS_FILE: str = "seed_cards.json"
    GOLDEN_SAMPLES_FILE: str = "golden_samples.jsonl"
    MAX_INPUT_LENGTH: int = 5000
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    DATA_DIR: str = "./data"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_chroma_path(self) -> Path:
        return Path(self.CHROMA_PERSIST_DIR)

    def get_data_path(self, filename: str = "") -> Path:
        base_path = Path(self.DATA_DIR)
        if filename:
            return base_path / filename
        return base_path


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
