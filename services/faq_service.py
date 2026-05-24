import os
import json
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.openai_client import send_chat


def load_sop(filepath: Optional[str] = None) -> Dict[str, Any]:
    """Reads the SOP JSON file and returns it as a Python dictionary.

    Args:
        filepath: Optional path to the SOP JSON file. Defaults to 'data/sop.json'
            relative to this project structure.

    Returns:
        A dictionary containing the structured SOP data.
    """
    if filepath is None:
        # Resolve path relative to this file's location (services/faq_service.py -> ../data/sop.json)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "data", "sop.json")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_system_prompt(filepath: Optional[str] = None) -> str:
    """Reads the system prompt template file.

    Args:
        filepath: Optional path to the system prompt file. Defaults to
            'prompts/system_prompt.txt'.

    Returns:
        The content string of the system prompt.
    """
    if filepath is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "prompts", "system_prompt.txt")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _escalate_on_error(reason: str) -> Dict[str, Any]:
    """Fail-safe response used whenever the service cannot produce a trusted
    answer. We deliberately escalate to a human rather than risk returning a
    fabricated or malformed answer — failing safe is the whole point.

    Args:
        reason: A short machine-readable tag describing what went wrong.

    Returns:
        A schema-valid escalation response dict.
    """
    return {
        "answer": "I'm sorry — I hit an issue processing that. I'm passing you to "
                  "a human teammate who can help.",
        "in_scope": False,
        "requires_escalation": True,
        "escalation_reason": reason,
    }


def answer_question(user_question: str) -> Dict[str, Any]:
    """Answers a user question using the SOP and the configured model.

    The function always returns a schema-valid dict, even on failure: any
    internal error fails safe to a human escalation rather than guessing.

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

    # Load SOP and system prompt.
    # Note: re-read from disk on each call. Fine (and stateless) for a demo;
    # in production the SOP would be loaded once at startup and passed in.
    sop = load_sop()
    system_prompt_template = load_system_prompt()


    full_system_prompt = (
        f"{system_prompt_template}\n\n"
        f"INJECTED CLINIC SOP DATA:\n"
        f"{json.dumps(sop, indent=2)}\n"
    )

    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_question},
    ]

    # --- Step 1: API call. A failure here is a transport/provider problem
    # (network, auth, rate limit, outage) — distinct from a bad response body. ---
    try:
        response_text = send_chat(
            messages=messages,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error(f"FAQ Service - API call failed: {e}")
        return _escalate_on_error(f"api_error: {e}")


    try:
        parsed_result = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"FAQ Service - Model returned non-JSON: {e}. Raw: {response_text!r}")
        return _escalate_on_error("invalid_json_from_model")

   
    required = {"answer", "in_scope", "requires_escalation", "escalation_reason"}
    if not required.issubset(parsed_result):
        logger.error(f"FAQ Service - Response missing required keys. Got: {list(parsed_result)}")
        return _escalate_on_error("malformed_schema")

    # Log metadata at INFO, full payload at DEBUG (avoids noisy terminal output).
    logger.info(
        f"FAQ Service - Parsed response metadata: "
        f"in_scope={parsed_result.get('in_scope')}, "
        f"requires_escalation={parsed_result.get('requires_escalation')}"
    )
    logger.debug(f"FAQ Service - Full parsed result: {parsed_result}")
    return parsed_result