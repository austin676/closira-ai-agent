import os
import json
from typing import Any, Dict, List, Optional
from utils.logger import logger
from utils.openai_client import send_chat


def load_summary_prompt(filepath: Optional[str] = None) -> str:
    """Reads the summary prompt template file.

    Returns:
        The content string of the summary prompt.
    """
    if filepath is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "prompts", "summary_prompt.txt")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def generate_summary(
    conversation_log: List[Dict[str, str]],
    qualification_answers: Optional[Dict[str, Any]],
    escalation_reasons: List[str],
) -> Dict[str, Any]:
    """Generates a structured JSON session summary via the model.

    Args:
        conversation_log: List of {"question": "...", "answer": "..."} dicts
                          from the FAQ turns.
        qualification_answers: Dict from qualification_service, or None.
        escalation_reasons: List of reason strings collected during the session.

    Returns:
        {
            "customer_intent": "...",
            "details_collected": { ... },
            "sop_gaps": [...],
            "recommended_next_action": "...",
        }
    """
    logger.info("Summary Service - Generating session summary.")

    prompt_template = load_summary_prompt()

    # Build session data block for the model
    session_data = {
        "conversation": conversation_log,
        "qualification": qualification_answers,
        "escalation_reasons": escalation_reasons,
    }

    messages = [
        {"role": "system", "content": prompt_template},
        {
            "role": "user",
            "content": (
                "Here is the full session data. Please generate the summary JSON.\n\n"
                f"{json.dumps(session_data, indent=2)}"
            ),
        },
    ]

    try:
        response_text = send_chat(
            messages=messages,
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response_text)
        logger.info("Summary Service - Summary generated successfully.")
        logger.debug(f"Summary Service - Full summary: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"Summary Service - Exception: {e}")
        return {
            "customer_intent": "Unable to generate summary.",
            "details_collected": {},
            "sop_gaps": [],
            "recommended_next_action": f"Error: {str(e)}",
        }
