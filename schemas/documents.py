from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from db.models import DocumentType, DocumentStatus
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    # Response after uploading a document.
    id: UUID
    filename: str
    file_type: DocumentType
    file_size: int
    status: DocumentStatus
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    # Full document response.
    id: UUID
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size: int
    title: Optional[str] = None
    page_count: Optional[int] = None
    chunk_count: Optional[int] = None
    status: DocumentStatus
    error_message: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    # Response for document list.
    documents: List[DocumentResponse]
    total: int


class KnowledgeSearchResponse(BaseModel):
    # Response for knowledge base search.
    answer: str
    sources: List[Dict[str, Any]]
    doc_count: int
    retrieved_documents: List[Dict[str, Any]] = []
    error: Optional[bool] = None


class CollectionStatsResponse(BaseModel):
    # Response for collection statistics.
    name: str
    count: int
    status: str
