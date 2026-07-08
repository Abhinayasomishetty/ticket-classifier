
# Embedding service using HuggingFace models.
# Loads model once and reuses for all embedding operations.
from typing import List
from llama_index.core import Settings as LlamaSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from core.config import get_settings

settings = get_settings()
print(settings)
print(settings.__class__.__module__)
print(dir(settings))

# Global embedding model instance (loaded once)
_embedder: HuggingFaceEmbedding = None


def get_embedder() -> HuggingFaceEmbedding:
    """Get or create the embedding model singleton."""
    global _embedder
    
    if _embedder is None:
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}...")
        _embedder = HuggingFaceEmbedding(
            model_name=settings.EMBEDDING_MODEL,
            cache_folder="./models/embeddings",
            embed_batch_size=32
        )
        print("Embedding model loaded successfully!")
    
    return _embedder


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for a list of texts."""
    embedder = get_embedder()
    return embedder.get_text_embedding_batch(texts)


def get_embedding(text: str) -> List[float]:
    """Get embedding for a single text."""
    embedder = get_embedder()
    return embedder.get_text_embedding(text)