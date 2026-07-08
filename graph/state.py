from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add

class TicketState(TypedDict):
    """The state object passed between LangGraph nodes."""
    ticket_id: str
    title: str
    description: str
    
    # Classification Node outputs
    category: Optional[str]
    priority: Optional[str]
    confidence_score: Optional[str]
    reasoning: Optional[str]
    
    # Knowledge Node outputs
    knowledge_answer: Optional[str]
    knowledge_sources: Optional[List[Dict[str, Any]]]
    
    # Log Analysis Node outputs
    log_insights: Optional[str]

    # Phase 4: Resolution & Human Approval outputs
    proposed_action: Optional[str]
    proposed_reason: Optional[str]
    approval_decision: Optional[str]      # approved / rejected
    tool_execution_result: Optional[str]
    
    # Execution tracking (uses `add` operator to append lists across nodes)
    execution_logs: Annotated[List[Dict[str, Any]], add]