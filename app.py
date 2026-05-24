import sys
import json
from utils.logger import logger
from services.faq_service import answer_question
from services.escalation_service import evaluate_escalation
from services.qualification_service import run_qualification
from services.summary_service import generate_summary


def main():
    logger.info("Closira agent starting...")

    # Session state
    unanswered_count = 0
    conversation_log = []      
    escalation_reasons = []     
    qualification_answers = None


    # Phase 1 — FAQ turns (multi-turn loop)
    
    print("\n=== Bloom Aesthetics Clinic - FAQ Agent ===")
    print('Type "done" to finish FAQ and move to qualification.\n')

    # Support single-shot mode via CLI args
    cli_question = None
    if len(sys.argv) > 1:
        cli_question = " ".join(sys.argv[1:])

    while True:
        # Get user question
        if cli_question is not None:
            question = cli_question
            cli_question = None  # Only use CLI arg for the first turn
        else:
            try:
                question = input("You: ")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break

        stripped = question.strip().lower()
        if not stripped:
            continue
        if stripped == "done":
            break

        # Step 1 — Get FAQ answer
        faq_result = answer_question(question)

        # Update unanswered counter
        if not faq_result.get("in_scope", True):
            unanswered_count += 1

        # Step 2 — Evaluate escalation
        escalation = evaluate_escalation(
            user_message=question,
            faq_result=faq_result,
            unanswered_count=unanswered_count,
        )

        # Record to session log
        conversation_log.append({
            "question": question,
            "answer": faq_result.get("answer", ""),
        })

        if escalation["should_escalate"] and escalation["reason"]:
            escalation_reasons.append(escalation["reason"])

        # Print FAQ answer
        answer_text = faq_result.get("answer", "")
        print(f"\nAgent: {answer_text}")

        if escalation["should_escalate"]:
            print(f"  [!] Escalation: {escalation['reason']}")

        print()

    # ---------------------------------------------------------------
    # Phase 2 — Qualification
    # ---------------------------------------------------------------
    if conversation_log:
        print("\n=== Qualification ===")
        print("Before we wrap up, a few quick questions:\n")

        qualification_answers = run_qualification()

        print("\n--- Qualification Collected ---")
        print(json.dumps(qualification_answers, indent=2, ensure_ascii=False))
        print("-------------------------------")

    # ---------------------------------------------------------------
    # Phase 3 — Session Summary
    # ---------------------------------------------------------------
    if conversation_log:
        print("\n=== Session Summary ===")

        summary = generate_summary(
            conversation_log=conversation_log,
            qualification_answers=qualification_answers,
            escalation_reasons=escalation_reasons,
        )

        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print("=======================\n")

    logger.info("Closira agent session complete.")


if __name__ == "__main__":
    main()
