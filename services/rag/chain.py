# RAG chain: Combine retrieved documents with LLM to generate answers.
import json
import httpx
from typing import List, Dict, Any, Optional
from services.rag.retriever import query_documents
from core.config import get_settings

settings = get_settings()

RAG_PROMPT_TEMPLATE = """You are a helpful support assistant. Use the following knowledge base documents to answer the user's question.

If the documents don't contain relevant information, say so clearly. Don't make up information.

=== KNOWLEDGE BASE DOCUMENTS ===
{context}

=== USER QUESTION ===
{question}

=== INSTRUCTIONS ===
1. Answer based ONLY on the provided documents
2. Cite the source document name when possible
3. If no relevant info found, say "I couldn't find relevant information in the knowledge base"
4. Keep your answer concise and actionable

ANSWER:"""


async def generate_rag_answer(
    question: str, retrieved_docs: List[Dict[str, Any]], category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an answer using RAG: retrieved docs + LLM.

    Args:
        question: User's question
        retrieved_docs: Documents retrieved from vector store
        category: Optional category for metadata filtering

    Returns:
        Dict with 'answer', 'sources', 'doc_count'
    """
    if not retrieved_docs:
        return {
            "answer": "No relevant documents found in the knowledge base.",
            "sources": [],
            "doc_count": 0,
        }

    # Build context from retrieved documents
    context_parts = []
    sources = []

    for i, doc in enumerate(retrieved_docs, 1):
        source_name = doc["metadata"].get("filename", f"Document {i}")
        page = doc["metadata"].get("page", "N/A")

        context_parts.append(
            f"--- {source_name} (Page: {page}, Relevance: {doc['score']}) ---\n{doc['text']}"
        )
        sources.append({"filename": source_name, "page": page, "score": doc["score"]})

    context = "\n\n".join(context_parts)

    # Build the full prompt
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    print("=" * 50)
    print("PROMPT SENT TO OLLAMA")
    print(prompt)
    print("=" * 50)

    # Call Llama-3
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print("=" * 60)
            print("Sending request to:", f"{settings.OLLAMA_BASE_URL}/api/generate")
            print("Model:", settings.OLLAMA_MODEL)
            print("=" * 60)
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower for factual answers
                        "top_p": 0.9,
                    },
                },
            )
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "").strip()

            return {
                "answer": answer,
                "sources": sources,
                "doc_count": len(retrieved_docs),
            }

        # except httpx.HTTPError as e:
        #     return {
        #         "answer": f"Error generating answer: {str(e)}",
        #         "sources": sources,
        #         "doc_count": len(retrieved_docs),
        #         "error": True
        #     }
        except Exception as e:
            import traceback

            print("=" * 60)
            print("OLLAMA ERROR")
            traceback.print_exc()
            print("=" * 60)

            return {
                "answer": f"Error generating answer: {repr(e)}",
                "sources": sources,
                "doc_count": len(retrieved_docs),
                "error": True,
            }


async def search_knowledge_for_ticket(
    ticket_title: str,
    ticket_description: str,
    category: Optional[str] = None,
    top_k: Optional[int] = None,
) -> Dict[str, Any]:
    """
    High-level function: Search knowledge base for a ticket.

    Combines retrieval + generation in one call.
    """
    # Build search query from ticket
    search_query = f"{ticket_title}. {ticket_description}"

    # Build metadata filter based on category
    where_filter = None
    if category:
        where_filter = {"category": category.lower()}

    # Retrieve relevant documents
    retrieved_docs = query_documents(
        query=search_query, top_k=top_k or 1, where_filter=None
    )
    print("=" * 50)
    print("Retrieved Docs:", len(retrieved_docs))

    for i, doc in enumerate(retrieved_docs):
        print(f"\nDocument {i+1}")
        print("Score:", doc["score"])
        print("Metadata:", doc["metadata"])
        print("Text:", doc["text"][:300])

        print("=" * 50)

    # Generate answer using RAG
    result = await generate_rag_answer(
        question=f"How should we handle this ticket? {ticket_title} - {ticket_description}",
        retrieved_docs=retrieved_docs,
        category=category,
    )

    # Add raw retrieved docs for reference
    result["retrieved_documents"] = [
        {
            "text": (
                doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"]
            ),
            "score": doc["score"],
            "filename": doc["metadata"].get("filename"),
        }
        for doc in retrieved_docs
    ]
    return result
