from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import time
from sqlalchemy import desc
from db.database import get_db
from db.models import Ticket, User,AgentExecution,ExecutionStatus
from schemas.api.routes.auth import get_current_user
from core.classifier import classify_ticket
from schemas.tickets import (
    TicketCreate,
    TicketResponse,
    TicketListResponse,
    TicketProcessResponse,
    ExecutionLogResponse,
)
from schemas.documents import KnowledgeSearchResponse
from schemas.api.routes.documents import search_knowledge


router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create a new ticket.
    # The ticket will be automatically classified by Llama-3.

    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        user_id=current_user.id
    )

    # Measure classifier time
    start = time.time()
    # now ai starts working
    classification = await classify_ticket(
        ticket_data.title,
        ticket_data.description
    )

    print(f"Classifier took {time.time() - start:.2f} seconds")

    # Apply classification
    ticket.category = classification["category"]
    ticket.priority = classification["priority"]
    ticket.confidence_score = classification["confidence_score"]
    ticket.classification_reasoning = classification["reasoning"]

    # Save ticket
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

@router.get("/", response_model=TicketListResponse)
def get_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: str = Query(None, description="Filter by category"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all tickets for the current user.
    # Supports pagination and filtering.
    query = db.query(Ticket).filter(Ticket.user_id == current_user.id)
    
    # Apply filters
    if category:
        query = query.filter(Ticket.category == category.lower())
    if status:
        query = query.filter(Ticket.status == status.lower())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    tickets = query.order_by(desc(Ticket.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "tickets": tickets,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get a specific ticket by ID.
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == current_user.id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return ticket

# NEW: Quick search knowledge for a ticket (shortcut endpoint)
@router.post("/{ticket_id}/search-knowledge")
async def ticket_search_knowledge(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Shortcut endpoint to search knowledge base for a ticket.
    # Delegates to /documents/tickets/{id}/search-knowledge
    
    
    return await search_knowledge(ticket_id, db, current_user)




@router.post("/{ticket_id}/search-knowledge")
async def ticket_search_knowledge(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await search_knowledge(ticket_id, db, current_user)