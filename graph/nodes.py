import time
import httpx
import json
from typing import Dict, Any
from graph.state import TicketState
from core.config import get_settings
from core.classifier import classify_ticket
from services.rag.chain import search_knowledge_for_ticket
from tools.action_tools import execute_tool

settings = get_settings()

def log_node_execution(state: TicketState, node_name: str, status: str, output: Any, duration_ms: int, error: str = None) -> Dict[str, Any]:
    """Helper to format execution logs consistently."""
    log = {
        "node_name": node_name,
        "status": status,
        "duration_ms": duration_ms,
        "output": output if not error else None,
        "error": error
    }
    return {"execution_logs": [log]}

async def classifier_node(state: TicketState) -> Dict[str, Any]:
    """Node 1: Classifies the ticket using Llama-3."""
    start_time = time.time()
    try:
        result = await classify_ticket(state["title"], state["description"])
        duration = int((time.time() - start_time) * 1000)
        
        output = {
            "category": result["category"].value,
            "priority": result["priority"].value,
            "confidence": result["confidence_score"]
        }
        
        logs = log_node_execution(state, "Classifier", "success", output, duration)
        
        return {
            "category": result["category"].value,
            "priority": result["priority"].value,
            "confidence_score": result["confidence_score"],
            "reasoning": result["reasoning"],
            **logs
        }
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        logs = log_node_execution(state, "Classifier", "error", None, duration, str(e))
        return {"category": "other", "priority": "medium", "reasoning": "Agent failed", **logs}

async def knowledge_node(state: TicketState) -> Dict[str, Any]:
    """Node 2: Searches RAG knowledge base based on classification."""
    start_time = time.time()
    try:
        result = await search_knowledge_for_ticket(
    ticket_title=state["title"],
    ticket_description=state["description"],
    category=state.get("category")
)
        
        duration = int((time.time() - start_time) * 1000)
        
        output = {"sources_found": len(result.get("sources", [])), "answer_preview": result.get("answer", "")[:100]}
        logs = log_node_execution(state, "Knowledge_RAG", "success", output, duration)
        
        return {
            "knowledge_answer": result.get("answer"),
            "knowledge_sources": result.get("sources", []),
            **logs
        }
    except Exception as e:
        print("=" * 60)
        print("KNOWLEDGE NODE ERROR")
        print(e)
        print("=" * 60)
        duration = int((time.time() - start_time) * 1000)
        logs = log_node_execution(state, "Knowledge_RAG", "error", None, duration, str(e))
        return {"knowledge_answer": "Knowledge search failed", "knowledge_sources": [], **logs}

async def log_analysis_node(state: TicketState) -> Dict[str, Any]:
    """Node 3: Analyzes ticket description for logs, stack traces, or technical clues."""
    start_time = time.time()
    prompt = f"""Analyze the following support ticket for any technical logs, stack traces, error codes, or system clues.
    
Ticket Title: {state['title']}
Ticket Description: {state['description']}
Category: {state.get('category', 'Unknown')}

If technical logs or errors are present, extract the root cause and summarize the technical issue.
If no logs are present, respond with exactly: 'NO_LOGS_FOUND'

ANSWER:"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}
            )
            response.raise_for_status()
            insights = response.json().get("response", "").strip()
            
        duration = int((time.time() - start_time) * 1000)
        has_logs = "NO_LOGS_FOUND" not in insights
        output = {"has_logs": has_logs}
        logs = log_node_execution(state, "Log_Analyzer", "success", output, duration)
        
        return {"log_insights": insights, **logs}
    except Exception as e:
       print("=" * 60)
       print("LOG ANALYZER ERROR")
       print(e)
       print("=" * 60)

       duration = int((time.time() - start_time) * 1000)
       logs = log_node_execution(state, "Log_Analyzer", "error", None, duration, str(e))
       return {
          "log_insights":f"Error:{repr(e)}",**logs
          **logs
    }

