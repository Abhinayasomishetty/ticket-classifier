from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ticket Classifier"
    DEBUG: bool = True
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/ticket_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Llama 3 (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"  # where chromabd stores embeddings
    CHROMA_COLLECTION_NAME: str = "knowledge_base"  # its like a table name

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384

    # Document Storage
    DOCUMENT_UPLOAD_DIR: str = "./data/documents"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: list = [".pdf", ".docx", ".txt"]

    # RAG
    RAG_TOP_K: int = 3
    RAG_SIMILARITY_THRESHOLD: float = 0.3

    @property
    def document_upload_path(self) -> Path:
        path = Path(self.DOCUMENT_UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_persist_path(self) -> Path:
        path = Path(self.CHROMA_PERSIST_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
