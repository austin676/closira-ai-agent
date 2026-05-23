import os
import json
from typing import Dict, Any
from utils.logger import logger
from utils.openai_client import send_chat

def load_sop(filepath: str = None) -> Dict[str, Any]:
    """Reads the SOP JSON file and returns it as a Python dictionary.

    Args:
        filepath: Optional path to the SOP JSON file. Defaults to 'data/sop.json' relative to this project structure.

    Returns:
        A dictionary containing the structured SOP data.
    """
    if filepath is None:
        # Resolve path relative to this file's location (services/faq_service.py -> ../data/sop.json)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "data", "sop.json")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_system_prompt(filepath: str = None) -> str:
    """Reads the system prompt template file.

    Args:
        filepath: Optional path to the system prompt file. Defaults to 'prompts/system_prompt.txt'.

    Returns:
        The content string of the system prompt.
    """
    if filepath is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "prompts", "system_prompt.txt")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def answer_question(user_question: str) -> Dict[str, Any]:
    """Answers a user question using the SOP and Gemini.

    Args:
        user_question: The question asked by the user.

    Returns:
        A dictionary representing the parsed JSON response:
        {
            "answer": "...",
            "in_scope": bool,
            "requires_escalation": bool,
            "escalation_reason": str or None
        }
    """
    logger.info("FAQ Service - Request received.")
    logger.debug(f"FAQ Service - User Question: {user_question}")

    # Load SOP and system prompt
    sop = load_sop()
    system_prompt_template = load_system_prompt()

    # Inject SOP into system prompt
    full_system_prompt = (
        f"{system_prompt_template}\n\n"
        f"INJECTED CLINIC SOP DATA:\n"
        f"{json.dumps(sop, indent=2)}\n"
    )

    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_question}
    ]

    try:
        response_text = send_chat(
            messages=messages,
            response_format={"type": "json_object"}
        )
        parsed_result = json.loads(response_text)
        
        # Log metadata at INFO level, and full payload at DEBUG level to avoid duplication in terminal
        logger.info(
            f"FAQ Service - Parsed response metadata: "
            f"in_scope={parsed_result.get('in_scope')}, "
            f"requires_escalation={parsed_result.get('requires_escalation')}"
        )
        logger.debug(f"FAQ Service - Full parsed result: {parsed_result}")
        return parsed_result
        
    except Exception as e:
        logger.error(f"FAQ Service - Exception occurred: {e}")
        return {
            "answer": "I apologize, but I encountered an issue processing your request. I am escalating this to our human team to assist you further.",
            "in_scope": False,
            "requires_escalation": True,
            "escalation_reason": f"error: {str(e)}"
        }
