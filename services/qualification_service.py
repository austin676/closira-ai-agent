import os
import json
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.openai_client import send_chat


# The 3 qualification questions, asked in order
QUALIFICATION_QUESTIONS = [
    "What type of service are you interested in? (e.g., Botox, Fillers, Consultation, other)",
    "How many people will be attending, or is this just for yourself?",
    "Have you had any aesthetic treatments before, and if so, where?",
]

# Keys that map to each question's answer in the result dict
QUALIFICATION_KEYS = [
    "service_interest",
    "party_size",
    "prior_experience",
]


def load_qualification_prompt(filepath: Optional[str] = None) -> str:
    """Reads the qualification prompt template file.

    Returns:
        The content string of the qualification prompt.
    """
    if filepath is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "prompts", "qualification_prompt.txt")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def run_qualification() -> Dict[str, Any]:
    """Runs the 3-question qualification flow interactively.

    Asks each question in sequence, collects the user's typed answers,
    and returns them as a structured dict.

    Returns:
        {
            "service_interest": "...",
            "party_size": "...",
            "prior_experience": "...",
        }
    """
    logger.info("Qualification Service - Starting qualification flow.")

    answers: Dict[str, Any] = {}

    for i, question in enumerate(QUALIFICATION_QUESTIONS):
        key = QUALIFICATION_KEYS[i]

        print(f"\n  Q{i + 1}: {question}")
        try:
            answer = input("  > ")
        except (KeyboardInterrupt, EOFError):
            logger.warning("Qualification Service - User exited during qualification.")
            break

        answers[key] = answer.strip() if answer.strip() else None

    logger.info(f"Qualification Service - Collected answers: {answers}")
    return answers


def run_qualification_via_model(user_answers: List[str]) -> Dict[str, Any]:
    """Alternative: feeds pre-collected answers through the model with the
    qualification prompt to get structured JSON back.

    Args:
        user_answers: List of 3 raw answer strings (one per question).

    Returns:
        Parsed qualification dict from model output.
    """
    prompt_template = load_qualification_prompt()

    # Build a conversation with the user's answers inline
    conversation = ""
    for i, question in enumerate(QUALIFICATION_QUESTIONS):
        conversation += f"Q: {question}\n"
        if i < len(user_answers):
            conversation += f"A: {user_answers[i]}\n"

    messages = [
        {"role": "system", "content": prompt_template},
        {
            "role": "user",
            "content": (
                "Here are the qualification answers collected:\n\n"
                f"{conversation}\n"
                "Please return the structured JSON summary."
            ),
        },
    ]

    try:
        response_text = send_chat(
            messages=messages,
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response_text)
        logger.info(f"Qualification Service (model) - Parsed: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"Qualification Service (model) - Exception: {e}")
        return {
            "service_interest": None,
            "party_size": None,
            "prior_experience": None,
        }
