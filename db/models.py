import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from db.database import Base
import enum


class TicketCategory(str, enum.Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SUPPORT = "support"
    BILLING = "billing"
    OTHER = "other"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ExecutionStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tickets = relationship("Ticket", back_populates="created_by")
    documents = relationship("Document", back_populates="uploaded_by")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Classification fields (populated by Llama-3)
    category = Column(Enum(TicketCategory), nullable=True)
    priority = Column(Enum(TicketPriority), nullable=True)
    confidence_score = Column(String(10), nullable=True)  # e.g., "0.85"
    classification_reasoning = Column(Text, nullable=True)

    # Metadata
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    created_by = relationship("User", back_populates="tickets")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)

    title = Column(String(500), nullable=True)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)

    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(Text, nullable=True)

    chroma_collection = Column(String(100), nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_by = relationship("User", back_populates="documents")


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    node_name = Column(String(100), nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.RUNNING)
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", backref="agent_executions")


class AuditAction(str, enum.Enum):
    STATUS_CHANGE = "status_change"
    NOTE_ADDED = "note_added"
    TICKET_ESCALATED = "ticket_escalated"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)

    action = Column(Enum(AuditAction), nullable=False)

    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)

    note = Column(Text, nullable=True)

    performed_by = Column(String(100), default="system")

    timestamp = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", backref="audit_logs")
