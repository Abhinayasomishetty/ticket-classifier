import uuid
import os
import shutil
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Document, DocumentType, DocumentStatus, User, Ticket
from schemas.api.routes.auth import get_current_user
from services.rag.parser import parse_document, create_llama_documents
from services.rag.retriever import (
    add_documents,
    delete_document as delete_from_chroma,
    get_collection_stats,
)
from services.rag.chain import search_knowledge_for_ticket
from schemas.documents import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    KnowledgeSearchResponse,
    CollectionStatsResponse,
)
from core.config import get_settings
from pathlib import Path

settings = get_settings()
router = APIRouter(prefix="/documents", tags=["Documents"])


def get_file_type(filename: str) -> DocumentType:
    # Determine document type from filename.
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    type_map = {
        "pdf": DocumentType.PDF,
        "docx": DocumentType.DOCX,
        "txt": DocumentType.TXT,
    }

    return type_map.get(ext)


async def process_document_background(doc_id: str, db: Session):
    # Process document: parse, chunk, embed, store in ChromaDB.
    # Called after file upload.

    from sqlalchemy import select

    # Get document from DB
    doc = db.execute(select(Document).where(Document.id == doc_id)).scalar_one_or_none()
    if not doc:
        return

    # Update status to processing
    doc.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        # Parse document
        chunks, metadata = parse_document(doc.file_path)

        if not chunks:
            raise ValueError("No text content could be extracted from the document")

        # Create LlamaIndex documents
        llama_docs = create_llama_documents(
            chunks=chunks, filename=doc.original_filename, doc_id=str(doc.id)
        )
        # Add to ChromaDB
        add_documents(llama_docs, settings.CHROMA_COLLECTION_NAME)

        # Update document record
        doc.status = DocumentStatus.COMPLETED
        doc.page_count = metadata.get("page_count")
        doc.chunk_count = len(chunks)
        doc.chroma_collection = settings.CHROMA_COLLECTION_NAME
        doc.processed_at = datetime.utcnow()

        # Try to extract title from first chunk
        if chunks and not doc.title:
            doc.title = chunks[0][:200].replace("\n", " ")

        db.commit()

        print(
            f"Document {doc.original_filename} processed successfully: {len(chunks)} chunks"
        )

    except Exception as e:
        doc.status = DocumentStatus.FAILED
        doc.error_message = str(e)[:1000]
        db.commit()
        print(f"Error processing document {doc.original_filename}: {e}")


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, DOCX, or TXT file"),
    category: Optional[str] = Query(None, description="Category to tag documents with"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Upload a document to the knowledge base.

    # Supported formats: PDF, DOCX, TXT
    # Max file size: 50MB

    # Validate file type
    file_type = get_file_type(file.filename)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {settings.ALLOWED_FILE_TYPES}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Generate unique filename
    doc_id = str(uuid.uuid4())
    ext = file.filename.rsplit(".", 1)[-1].lower()
    unique_filename = f"{doc_id}.{ext}"
    upload_dir = Path(settings.DOCUMENT_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    document = Document(
        id=doc_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        file_type=file_type,
        status=DocumentStatus.PENDING,
        user_id=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Process document in background (synchronous for now)
    # In production, use Celery or FastAPI BackgroundTasks

    asyncio.create_task(process_document_background(doc_id, db))

    return document


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # List all uploaded documents.
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if status:
        query = query.filter(Document.status == status.lower())

    total = query.count()
    offset = (page - 1) * page_size
    documents = (
        query.order_by(Document.uploaded_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {"documents": documents, "total": total}


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get a specific document by ID.
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Delete a document from the knowledge base.
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Delete from ChromaDB
    if doc.status == DocumentStatus.COMPLETED:
        # Delete all chunks associated with this document
        # Note: In a production system, you'd track chunk IDs
        try:
            delete_from_chroma(document_id, doc.chroma_collection)
        except Exception as e:
            print(f"Error deleting from ChromaDB: {e}")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from database
    db.delete(doc)
    db.commit()

    return None


@router.get("/stats/collection", response_model=CollectionStatsResponse)
def get_stats(current_user: User = Depends(get_current_user)):
    # Get knowledge base collection statistics.
    return get_collection_stats()


async def search_knowledge(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Search the knowledge base for relevant information about a ticket.

    # Uses the ticket's title, description, and classification to find
    # relevant documents and generate an AI answer.

    # Get ticket
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.user_id == current_user.id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    # Check if knowledge base has documents
    stats = get_collection_stats()
    if stats["count"] == 0:
        return KnowledgeSearchResponse(
            answer="The knowledge base is empty. Please upload some documents first.",
            sources=[],
            doc_count=0,
            retrieved_documents=[],
        )

    # Search knowledge base
    result = await search_knowledge_for_ticket(
        ticket_title=ticket.title,
        ticket_description=ticket.description,
        category=ticket.category.value if ticket.category else None,
    )

    # Update ticket with search results
    ticket.relevant_documents = [
        doc["filename"] for doc in result["sources"] if doc.get("filename")
    ]
    ticket.knowledge_summary = result["answer"][:2000]  # Truncate for DB
    db.commit()

    return result
