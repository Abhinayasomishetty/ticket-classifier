import uuid
from typing import List, Optional, Dict, Any
from chromadb import Client, PersistentClient
from chromadb.config import Settings as ChromaSettings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Document as LlamaDocument
from services.rag.embedder import get_embedder
from core.config import get_settings, Settings


settings = get_settings()

# Global ChromaDB client
_chroma_client: PersistentClient = None
_vector_store: ChromaVectorStore = None


def get_chroma_client() -> PersistentClient:
    # Get or create the ChromaDB client singleton.
    global _chroma_client
    print("Inside get_chroma_client")
    print(settings)
    print(type(settings))
    print(dir(settings))
    if _chroma_client is None:
        _chroma_client = PersistentClient(
            path=str(settings.chroma_persist_path),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

    return _chroma_client


def get_vector_store(collection_name: Optional[str] = None) -> ChromaVectorStore:
    # Get or create a ChromaDB vector store.
    global _vector_store

    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
    chroma_client = get_chroma_client()

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )
    print("Collection count:", collection.count())

    _vector_store = ChromaVectorStore(chroma_collection=collection)
    return _vector_store


def add_documents(
    documents: List[LlamaDocument],
    collection_name: Optional[str] = None,
    doc_ids: Optional[List[str]] = None,
) -> int:
    print("INSIDE add documents")
    print("Documents received:", len(documents))
    for d in documents:
        print("Text:", d.text)
    """
    Add documents to the vector store.
    
    Args:
        documents: List of LlamaIndex Document objects
        collection_name: ChromaDB collection name
        doc_ids: Optional list of document IDs
    
    Returns:
        Number of documents added
    """
    vector_store = get_vector_store(collection_name)
    embedder = get_embedder()

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    print("Documents received:", len(documents))
    for d in documents:
        print("TEXT:", d.text)
    # Create index with custom embedder

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embedder,
        show_progress=False,
    )

    print(index)
    collection = get_chroma_client().get_collection(
        collection_name or settings.CHROMA_COLLECTION_NAME
    )

    return len(documents)


def query_documents(
    query: str,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None,
    collection_name: Optional[str] = None,
    where_filter: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    print("INSIDE query_document")
    """
    Query the vector store for similar documents.
    
    Args:
        query: The search query
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score (0-1)
        collection_name: ChromaDB collection name
        where_filter: ChromaDB where clause for metadata filtering
    
    Returns:
        List of dicts with 'text', 'score', 'metadata'
    """
    top_k = top_k or settings.RAG_TOP_K
    similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

    chroma_client = get_chroma_client()
    collection = chroma_client.get_collection(collection_name)
    print("=" * 50)
    print("Collection Name:", collection_name)
    print("Collection Count:", collection.count())
    print("Similarity Threshold:", similarity_threshold)
    print("=" * 50)
    print("===PEEK===")
    print(collection.peek(limit=5))

    data = collection.get(include=["documents", "metadatas", "embeddings"])

    print("Stored IDs:", len(data["ids"]))
    print("First ID:", data["ids"][:3])
    print("First Document:", data["documents"][:1])
    print("First Metadata:", data["metadatas"][:1])
    print("Collection Name:", collection_name)
    print("Collection Count:", collection.count())
    embedder = get_embedder()

    # Get query embedding
    query_embedding = embedder.get_text_embedding(query)

    # Query ChromaDB
    print("Query:", query)
    print("Embedding length:", len(query_embedding))
    print("Embedding:", query_embedding[:5])
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )
    print("RESULTS =", results)
    print("Documents =", results["documents"])
    print("Distances =", results["distances"])
    print("Metadata =", results["metadatas"])

    # Process results
    formatted_results = []

    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}

            # Convert distance to similarity score (cosine: similarity = 1 - distance)
            similarity = 1 - distance

            print("Distance:", distance)
            print("Similarity:", similarity)
            print("Threshold:", similarity_threshold)
            # ifsimilarity >= similarity_threshold:
            formatted_results.append(
                {"text": doc, "score": round(similarity, 4), "metadata": metadata}
            )

    return formatted_results


def delete_document(doc_id: str, collection_name: Optional[str] = None) -> bool:
    """Delete a document from the vector store by ID."""
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
    chroma_client = get_chroma_client()

    try:
        collection = chroma_client.get_collection(collection_name)
        collection.delete(ids=[doc_id])
        return True
    except Exception as e:
        print(f"Error deleting document {doc_id}: {e}")
        return False


def get_collection_stats(collection_name: Optional[str] = None) -> Dict[str, Any]:
    """Get statistics about a collection."""
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
    chroma_client = get_chroma_client()

    try:
        collection = chroma_client.get_collection(collection_name)
        return {
            "name": collection_name,
            "count": collection.count(),
            "status": "active",
        }
    except Exception:
        return {"name": collection_name, "count": 0, "status": "not_found"}
