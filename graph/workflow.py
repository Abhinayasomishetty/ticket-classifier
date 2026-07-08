from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from graph.state import TicketState
from graph.nodes import (
    classifier_node,
    knowledge_node,
    log_analysis_node,
)

def build_ticket_graph() -> StateGraph:
    """Constructs and compiles the LangGraph workflow with HITL interrupt."""

    workflow = StateGraph(TicketState)
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("log_analysis", log_analysis_node)
    
    workflow.set_entry_point("classifier")
    workflow.add_edge("classifier", "knowledge")
    workflow.add_edge("knowledge", "log_analysis")
    workflow.set_finish_point("log_analysis")
    
    checkpointer = MemorySaver()
    
    app = workflow.compile(
        checkpointer=checkpointer,
    )
    
    return app

app_graph = build_ticket_graph()

async def run_graph_stream(ticket_id: str, title: str, description: str):
    config = {"configurable": {"thread_id": ticket_id}}
    
    initial_state = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "execution_logs": []
    }
