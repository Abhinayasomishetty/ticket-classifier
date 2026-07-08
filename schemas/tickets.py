from datetime import datetime
from typing import Optional,Any,List,Dict
from pydantic import BaseModel, Field
from db.models import TicketCategory, TicketPriority, TicketStatus
from uuid import UUID 


class TicketCreate(BaseModel):
    # Schema for creating a new ticket.
    title: str = Field(..., min_length=5, max_length=255, description="Ticket title")
    description: str = Field(..., min_length=10, description="Ticket description")


class TicketResponse(BaseModel):
    # Schema for ticket response.
    id: UUID
    title: str
    description: str
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    confidence_score: Optional[str] = None
    classification_reasoning: Optional[str] = None
    status: TicketStatus
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    relevant_documents: Optional[Any] = None
    knowledge_summary: Optional[str] = None
    log_analysis: Optional[str] = None
    
    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    # Schema for list of tickets.
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int


class ExecutionLogResponse(BaseModel):
    node_name: str
    status: str
    duration_ms: Optional[int] = None
    output: Optional[Dict[str, Any]] = None


class TicketProcessResponse(BaseModel):
    ticket_id: str
    message: str

    category: Optional[str] = None
    priority: Optional[str] = None

    knowledge_answer: Optional[str] = None
    relevant_documents: Optional[List[Dict[str, Any]]] = None
    log_analysis: Optional[str] = None

    execution_logs: List[ExecutionLogResponse]