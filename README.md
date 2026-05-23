# Closira AI Agent

A robust, fail-safe AI customer support agent for Bloom Aesthetics Clinic. This project demonstrates an architecture focused on grounding, safe-failure, and multi-layered escalation, ensuring the AI strictly adheres to the clinic's standard operating procedures (SOP).

## Overview

The Closira AI Agent is designed to act as a front-line support assistant for a small-to-medium business (SMB). It handles FAQ interactions, qualifies leads by asking structured questions, and generates a structured summary of the session for a human team to review.

Key features:
1. **Strict SOP Grounding:** The agent is instructed to use *only* the facts in `data/sop.json`.
2. **Two-Layer Escalation System:** Combines deterministic keyword rules (Layer 1) with semantic model evaluation (Layer 2) to ensure complaints, medical queries, or out-of-scope questions are always escalated to humans.
3. **Structured Lead Qualification:** Collects business intent, party size, and prior experience into a JSON object.
4. **Session Summarization:** At the end of the session, generates a clear JSON summary of customer intent, collected details, SOP gaps, and recommended next actions.

## Architecture

The project maintains a strict separation of concerns:

- `app.py`: The orchestrator. Handles the terminal UI loop and session state tracking. It contains no business logic.
- `services/`: Business logic layer.
  - `faq_service.py`: Handles multi-turn FAQ interactions and enforces JSON model responses.
  - `escalation_service.py`: Contains the dual-layer escalation evaluation logic.
  - `qualification_service.py`: Manages the 3-question qualification flow.
  - `summary_service.py`: Compiles the final session summary JSON.
- `utils/`: Infrastructure layer.
  - `openai_client.py`: A wrapper around the `google-genai` SDK (despite the name, it's a provider-agnostic wrapper currently using Gemini).
  - `logger.py`: Configured logging to suppress third-party noise.
- `prompts/`: Text templates defining the model's persona and constraints.
- `data/sop.json`: The source of truth for all factual answers.

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
1. **FAQ Phase:** Ask questions (e.g., "What are your hours?", "How much is Botox?"). The agent will respond. If a question is out-of-scope or triggers an escalation rule, it will gracefully escalate.
2. **Transition:** Type `done` to end the FAQ phase.
3. **Qualification Phase:** The agent will ask 3 quick questions to gather your details.
4. **Summary Phase:** A final JSON summary of the interaction is generated for the human team.

You can also run a single-turn question directly from the CLI:
```bash
python app.py "What are your services?"
```

## Escalation Logic & Grounding Strategy

For a deep dive into how the agent handles safety, hallucination mitigation, and its two-layer escalation system, see [Prompt Design & Architecture](prompt_design.md).

## Known Limitations

- **Terminal Output Encoding:** On Windows, emojis or certain unicode characters (like the British Pound £) may cause display issues depending on the active code page.
- **Stateless FAQ:** The current FAQ turn evaluates each question in isolation. Multi-turn context memory is partially handled by the `app.py` orchestration but not injected completely back into the `faq_service` prompt for complex follow-up referencing in the current build.
- **Latency:** Because the system uses structured JSON generation on every turn, response times are subject to the latency of the underlying LLM API.
