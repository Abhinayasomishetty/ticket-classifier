import json
import httpx
from typing import Optional
from core.config import get_settings
from db.models import TicketCategory, TicketPriority

settings = get_settings()

CLASSIFICATION_PROMPT = """
You are an IT Helpdesk Ticket Classifier.

Your task is to analyze the user's ticket and classify it accurately.

Ticket Title:
{title}

Ticket Description:
{description}

Available Categories:
- bug
- feature_request
- support
- billing
- other

Priority Rules:
- critical = security breach, phishing, account compromise, data loss, production outage
- high = major functionality broken, no workaround
- medium = normal issue with workaround
- low = question, guidance, minor enhancement

Instructions:
1. Read ONLY the given ticket.
2. Do NOT copy example text.
3. Do NOT invent information.
4. Return ONLY valid JSON.
5. Keep reasoning under 20 words.

Expected JSON:

{{
  "category":"bug",
  "priority":"medium",
  "confidence_score":"0.95",
  "reasoning":"Short explanation."
}}

Classification rules:
- BUG: Software defects, errors, crashes, unexpected behavior
- FEATURE_REQUEST: New functionality requests, enhancements
- SUPPORT: How-to questions, usage help, configuration issues
- BILLING: Payment issues, subscription problems, invoices
- OTHER: Anything that doesn't fit above
Examples:

Example 1
Ticket: "Application crashes when I click Save"
Category: bug
Priority: high

Example 2
Ticket: "I forgot my password. How can I reset it?"
Category: support
Priority: low

Example 3
Ticket: "I was charged twice for my subscription."
Category: billing
Priority: high

Example 4
Ticket: "Please add Dark Mode."
Category: feature_request
Priority: low

Example 5
Ticket: "Someone logged into my account without permission."
Category: other
Priority: critical

Priority rules:
- CRITICAL: System down, data loss, security breach
- HIGH: Major feature broken, no workaround
- MEDIUM: Feature degraded, workaround exists
- LOW: Minor issues, cosmetic problems
"""


async def classify_ticket(title: str, description: str) -> dict:
    """
    Classify a ticket using local Llama-3 via Ollama.
    description:str)->dict:
    Returns:
        dict with category, priority, confidence_score, reasoning
    """
    prompt = CLASSIFICATION_PROMPT.format(title=title, description=description)

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,  # Low temp for consistent classification
                        "top_p": 0.8,
                        "num_predict": 120,
                    },
                },
            )

            result = response.json()
            raw_response = result.get("response", "")

            # Parse the JSON from the response
            return parse_classification_response(raw_response)
        except httpx.HTTPError as e:
            print("FULL ERROR TYPE=", type(e))
            print("FULL ERROR REPR=", repr(e))
            raise
            return get_fallback_classification()
        except json.JSONDecodeError as e:
            print("JSON parse error:", e)
            return get_fallback_classification()
        except Exception as e:
            print("UNEXPECTED ERROR=", repr(e))
            return get_fallback_classification()


def parse_classification_response(raw_response: str) -> dict:

    # Try to extract JSON from the response
    # Sometimes LLMs add markdown code blocks
    clean_response = raw_response.strip()

    if "```json" in clean_response:
        clean_response = clean_response.split("```json")[1].split("```")[0]
    elif "```" in clean_response:
        clean_response = clean_response.split("```")[1].split("```")[0]

    data = json.loads(clean_response)

    # Validate and normalize
    try:
        category = TicketCategory(data["category"].lower())
    except (KeyError, ValueError):
        category = TicketCategory.OTHER

    try:
        priority = TicketPriority(data["priority"].lower())
    except (KeyError, ValueError):
        priority = TicketPriority.MEDIUM

    return {
        "category": category,
        "priority": priority,
        "confidence_score": data.get("confidence_score", "0.5"),
        "reasoning": data.get("reasoning", "Classification completed"),
    }


def get_fallback_classification() -> dict:

    return {
        "category": TicketCategory.OTHER,
        "priority": TicketPriority.MEDIUM,
        "confidence_score": "0.0",
        "reasoning": "Classification failed - using default values",
    }
