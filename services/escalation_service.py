import re
from typing import Any, Dict, Tuple
from utils.logger import logger


# ---------------------------------------------------------------------------
# Keyword lists for deterministic rule matching (Layer 1)
# ---------------------------------------------------------------------------

COMPLAINT_KEYWORDS = [
    "complaint", "complain", "unhappy", "dissatisfied", "disappointed",
    "terrible", "horrible", "awful", "disgusting", "unacceptable",
    "worst", "angry", "furious", "rude", "unprofessional",
    "refund", "sue", "lawyer", "report you",
]

HUMAN_REQUEST_KEYWORDS = [
    "talk to a human", "speak to someone", "speak to a person",
    "real person", "human agent", "manager", "supervisor",
    "talk to a manager", "speak to a manager", "escalate",
    "connect me to", "transfer me",
]

MEDICAL_KEYWORDS = [
    "side effect", "side effects", "allergic", "allergy", "reaction",
    "pain", "swelling", "bruise", "bruising", "infection",
    "pregnant", "pregnancy", "breastfeeding", "medication",
    "medical condition", "medical history", "blood thinner",
    "safe for me", "contraindication", "risk", "dangerous",
    "how long does it last", "recovery time", "healing",
    "injection", "dosage", "units",
]

PRICING_NEGOTIATION_KEYWORDS = [
    "discount", "cheaper", "deal", "negotiate", "lower price",
    "too expensive", "price match", "can you do it for",
    "best price", "any offers", "promotion", "coupon",
    "reduce the price", "bring the price down",
]


def _keyword_match(text: str, keywords: list) -> str | None:
    """Check if any keyword appears in the text (case-insensitive).

    Returns the matched keyword or None.
    """
    text_lower = text.lower()
    for keyword in keywords:
        # Use word-boundary matching to reduce false positives
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
        if pattern.search(text_lower):
            return keyword
    return None


# ---------------------------------------------------------------------------
# Layer 1 — Deterministic Python rules
# ---------------------------------------------------------------------------

def check_deterministic_rules(
    user_message: str,
    unanswered_count: int,
) -> Tuple[bool, str | None]:
    """Applies hard-coded escalation rules against the user message.

    Args:
        user_message: The raw text the user typed.
        unanswered_count: Running count of out-of-scope / unanswered questions
                          in this conversation so far.

    Returns:
        (should_escalate, reason_string) — reason is None when no rule fires.
    """
    # Rule 1 — complaint / anger
    match = _keyword_match(user_message, COMPLAINT_KEYWORDS)
    if match:
        return True, f"complaint_detected (keyword: '{match}')"

    # Rule 2 — explicit human-request
    match = _keyword_match(user_message, HUMAN_REQUEST_KEYWORDS)
    if match:
        return True, f"human_requested (keyword: '{match}')"

    # Rule 3 — medical question
    match = _keyword_match(user_message, MEDICAL_KEYWORDS)
    if match:
        return True, f"medical_question (keyword: '{match}')"

    # Rule 4 — pricing negotiation
    match = _keyword_match(user_message, PRICING_NEGOTIATION_KEYWORDS)
    if match:
        return True, f"pricing_negotiation (keyword: '{match}')"

    # Rule 5 — unanswered-question threshold (>2)
    if unanswered_count > 2:
        return True, f"unanswered_threshold_exceeded (count: {unanswered_count})"

    return False, None


# ---------------------------------------------------------------------------
# Layer 2 — Model signal (reads FAQ service output)
# ---------------------------------------------------------------------------

def check_model_signal(faq_result: Dict[str, Any]) -> Tuple[bool, str | None]:
    """Reads the model's own escalation flags from the FAQ response.

    Args:
        faq_result: The parsed dict returned by faq_service.answer_question().

    Returns:
        (should_escalate, reason_string) — reason is None when model didn't flag.
    """
    requires = faq_result.get("requires_escalation", False)
    in_scope = faq_result.get("in_scope", True)
    model_reason = faq_result.get("escalation_reason")

    if requires:
        return True, f"model_flagged (reason: {model_reason})"

    if not in_scope:
        return True, "model_out_of_scope"

    return False, None


# ---------------------------------------------------------------------------
# Public API — combines both layers
# ---------------------------------------------------------------------------

def evaluate_escalation(
    user_message: str,
    faq_result: Dict[str, Any],
    unanswered_count: int,
) -> Dict[str, Any]:
    """Decides whether to escalate based on deterministic rules AND model signal.

    Final decision = (any deterministic rule fired) OR (model flagged).

    Args:
        user_message: The raw text the user typed.
        faq_result: The parsed dict from faq_service.answer_question().
        unanswered_count: Running count of unanswered/out-of-scope questions.

    Returns:
        {
            "should_escalate": bool,
            "triggered_by": "layer1" | "layer2" | "both" | None,
            "reason": str | None,
        }
    """
    # Layer 1
    l1_escalate, l1_reason = check_deterministic_rules(user_message, unanswered_count)
    # Layer 2
    l2_escalate, l2_reason = check_model_signal(faq_result)

    should_escalate = l1_escalate or l2_escalate

    # Determine which layer(s) triggered
    if l1_escalate and l2_escalate:
        triggered_by = "both"
        reason = f"Layer 1: {l1_reason} | Layer 2: {l2_reason}"
    elif l1_escalate:
        triggered_by = "layer1"
        reason = f"Layer 1: {l1_reason}"
    elif l2_escalate:
        triggered_by = "layer2"
        reason = f"Layer 2: {l2_reason}"
    else:
        triggered_by = None
        reason = None

    # Log the decision every time
    if should_escalate:
        logger.info(f"Escalation Service - ESCALATE | Triggered by: {triggered_by} | {reason}")
    else:
        logger.info("Escalation Service - No escalation needed.")

    return {
        "should_escalate": should_escalate,
        "triggered_by": triggered_by,
        "reason": reason,
    }
