# Closira AI Agent

A robust, fail-safe AI customer support agent for Bloom Aesthetics Clinic. This project demonstrates an architecture focused on grounding, safe-failure, and multi-layered escalation, ensuring the AI strictly adheres to the clinic's standard operating procedures (SOP).

## Overview

The Closira AI Agent is designed to act as a front-line support assistant for a small-to-medium business (SMB). It handles FAQ interactions, qualifies leads by asking structured questions, and generates a structured summary of the session for a human team to review.

Key features:
1. **Strict SOP Grounding:** The agent is instructed to use *only* the facts in `data/sop.json`. It will not guess or fabricate information beyond the SOP.
2. **Two-Layer Escalation System:** Combines deterministic keyword rules (Layer 1) with semantic model evaluation (Layer 2) to ensure complaints, medical queries, pricing negotiations, or out-of-scope questions are always escalated to humans.
3. **Structured Lead Qualification:** Collects service interest, party size, and prior experience into a structured JSON object.
4. **Session Summarization:** At the end of the session, generates a clear JSON summary of customer intent, collected details, SOP gaps, and recommended next actions.

## Architecture

The project maintains a strict separation of concerns:

```
closira/
├── app.py                          # Orchestrator — session loop & state tracking (no business logic)
├── prompt_design.md                # Prompt engineering rationale & design decisions
├── data/
│   └── sop.json                    # Source of truth for all factual answers
├── prompts/
│   ├── system_prompt.txt           # Main FAQ agent persona & grounding rules
│   ├── qualification_prompt.txt    # Data-extraction prompt for lead qualification
│   └── summary_prompt.txt          # Session summarization prompt
├── services/
│   ├── faq_service.py              # SOP-grounded multi-turn FAQ handler
│   ├── escalation_service.py       # Two-layer escalation evaluation (deterministic + model)
│   ├── qualification_service.py    # 3-question lead qualification flow
│   └── summary_service.py          # Session summary generation
├── utils/
│   ├── openai_client.py            # Gemini API wrapper with OpenAI-style message schema
│   └── logger.py                   # Configured logging with third-party noise suppression
├── test_transcripts/               # Recorded end-to-end session transcripts
│   ├── in_scope.md                 # Normal answerable question
│   ├── out_of_scope.md             # Question not in SOP
│   ├── escalation.md               # Complaint triggering both escalation layers
│   ├── qualification.md            # Full qualification flow
│   └── summary.md                  # End-to-end summary generation
├── generate_transcripts.py         # Script to regenerate test transcripts
└── requirements.txt
```

**Key design notes:**
- `app.py` is the orchestrator. It handles the terminal UI loop and session state tracking. It contains no business logic.
- `utils/openai_client.py` wraps the `google-genai` SDK using OpenAI-style message schemas (`system`/`user` roles) for easy portability. The default model is `gemini-2.5-flash`.
- `utils/logger.py` configures a clean console logger and suppresses noisy logs from `google`, `httpx`, and `httpcore`.
- Each prompt in `prompts/` has a dedicated service in `services/` that loads and invokes it.

## Setup

1. **Clone the repository** and navigate to the project directory.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   Create a `.env` file in the root directory. Add your Gemini API key. *(Note: The project uses the Gemini API instead of the OpenAI API because OpenAI requires a paid key, whereas Gemini provides a generous free tier. The internal wrapper in `utils/openai_client.py` maintains OpenAI-style message schemas for easy portability.)*
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Run Instructions

To start the interactive agent session:
```bash
python app.py
```

### The Session Flow:
1. **FAQ Phase:** Ask questions (e.g., "What are your hours?", "How much is Botox?", "Where are you located?"). The agent will respond using only SOP data. If a question is out-of-scope or triggers an escalation rule, it will gracefully escalate.
2. **Transition:** Type `done` to end the FAQ phase.
3. **Qualification Phase:** The agent will ask 3 quick questions to gather your details (service interest, party size, prior experience).
4. **Summary Phase:** A final JSON summary of the interaction is generated for the human team.

You can also run a single-turn question directly from the CLI:
```bash
python app.py "What are your services?"
```

## Testing

To regenerate all test transcripts:
```bash
python generate_transcripts.py
```

This runs 5 predefined scenarios through the full pipeline and captures the complete output (including logs, escalation decisions, and summaries) into `test_transcripts/`. See [Prompt Design & Architecture](prompt_design.md#testing--validation) for details on what each transcript tests.

## Escalation Logic & Grounding Strategy

For a deep dive into how the agent handles safety, hallucination mitigation, its two-layer escalation system, and prompt design decisions, see [Prompt Design & Architecture](prompt_design.md).

## Known Limitations

- **Keyword Fragility (Layer 1):** Deterministic rules are brittle. "I am not angry" contains the keyword "angry" and might trigger a false positive escalation if the regex isn't careful.
- **Context Window:** Injecting the entire SOP into the system prompt on every turn is feasible for a small clinic SOP. If the SOP grows to thousands of pages, this architecture will require a vector database and RAG approach.
- **Stateless FAQ:** The current FAQ turn evaluates each question in isolation. Multi-turn context memory is partially handled by the `app.py` orchestration but not injected completely back into the `faq_service` prompt for complex follow-up referencing.
- **Latency:** Because the system uses structured JSON generation on every turn, response times are subject to the latency of the underlying LLM API.
- **Terminal Encoding:** On Windows, certain unicode characters (like £) may cause display issues depending on the active code page.
