# Prompt Design & Architecture

This document explains the rationale behind the AI agent's prompt engineering, grounding strategies, and system design for the Bloom Aesthetics Clinic FAQ agent.

## The System Prompt: Tone & Persona
The prompt defines the agent as a "support agent for Bloom Aesthetics Clinic." For a Small-to-Medium Business (SMB) like a clinic, the tone must strike a delicate balance: it needs to be warm, professional, and empathetic, while remaining completely unambiguous about the limits of its own knowledge. 

We explicitly forbid the agent from using conversational filler when it doesn't know the answer. The persona is designed to inspire trust by clearly communicating what the clinic *can* help with, rather than trying to feign omniscience.

## Grounding & "Safe-Failure" Strategy
A common mistake in prompt design is telling the model "never hallucinate." Models cannot easily conceptualize "hallucination" because they simply generate statistically probable text. 

Instead, our grounding strategy is built around **"fail-safe" rules**:
- **Explicit boundaries:** We instruct the model to answer using *only* facts present in the injected SOP.
- **Acknowledge gaps:** If a question is not covered by the SOP, the model is strictly forbidden from guessing. It must acknowledge the gap and signal an escalation.
- **Prefer escalation in ambiguity:** When in doubt, it is safer for a business to say "Let me get a human to clarify" than to invent a price or a medical fact that the clinic must later honor or be liable for.

By framing the instruction as "ground every answer in the SOP and fail safe," we give the model a concrete, operational rule rather than a philosophical abstract.

## Two-Layer Escalation Design
The system uses a two-layer escalation architecture:

1. **Layer 1: Deterministic Python Rules**
   - We use strict keyword matching for complaints, medical questions, pricing negotiation, and human requests.
   - **Why?** Models can be inconsistent. If a user types "I want to sue you", we cannot rely on a prompt to consistently flag it as an escalation. Deterministic rules provide an auditable, 100% reliable safety net for critical edge cases.

2. **Layer 2: Model Signal**
   - The model evaluates the interaction against the SOP and flags `requires_escalation` or sets `in_scope` to `false`.
   - **Why?** Deterministic rules cannot catch every nuanced complaint or out-of-scope question. The model provides semantic understanding that keyword matching lacks.

**Why they sit alongside each other:** This defense-in-depth approach ensures that obvious critical triggers are caught instantly by code, while nuanced ambiguities are caught by the model's semantic comprehension.

## Self-Reported Confidence is Weakly Calibrated
Why not just ask the model, "Are you confident in your answer?"
LLMs are notoriously poor at self-evaluating their own confidence. A model might confidently generate a fabricated medical answer. By shifting the evaluation from "Are you confident?" to "Does this answer exist explicitly in the provided JSON SOP?", we change a subjective confidence score into an objective text-matching task. The model is much better at determining if string X is present in dictionary Y than it is at evaluating its own epistemological certainty.

This is precisely why the `in_scope` flag is framed as *"Is the factual answer to this question present in the SOP?"* rather than *"Are you confident?"* — it converts a subjective self-assessment into an objective text-matching task the model can perform reliably.

## Structured Output Reasoning
The prompt strictly enforces a JSON output schema for every turn:
```json
{
  "answer": "...",
  "in_scope": true,
  "requires_escalation": false,
  "escalation_reason": null
}
```
**Why?** 
1. **Machine Readability:** The service layer needs to programmatically read flags (`requires_escalation`, `in_scope`) to trigger business logic (like updating the unanswered counter or triggering Layer 2 escalation).
2. **Forced Evaluation:** By forcing the model to generate boolean flags alongside its text answer, we force it to evaluate the query against the SOP *before* completing the turn.

## Multi-Prompt Architecture
Beyond the main FAQ support agent, the system uses specialized prompts for distinct pipeline tasks:

1. **Qualification Extraction (`qualification_prompt.txt`)**: 
   - **Role**: Data-extraction assistant.
   - **Strategy**: It strictly converts raw, free-text user answers into a structured JSON object (`service_interest`, `party_size`, `prior_experience`). It is explicitly instructed *not* to converse, infer, or hallucinate details not present in the user's input.

2. **Session Summarization (`summary_prompt.txt`)**:
   - **Role**: Session summarizer.
   - **Strategy**: At the end of an interaction, it synthesizes the conversation history, qualification details, and escalation reasons into a concise JSON summary for the human team. It is grounded by the rule to *only* list "sop_gaps" that actually occurred (flagged `in_scope: false`) during the session.

## Testing & Validation
To verify the agent's behavior across different scenarios, the project includes a `generate_transcripts.py` script. This script feeds predefined inputs into the full pipeline and captures the complete session output (including logs, escalation decisions, and summaries) into `test_transcripts/`. Five scenarios are covered:

| Transcript | What it tests |
|---|---|
| `in_scope.md` | Normal answerable question — model stays grounded |
| `out_of_scope.md` | Question not in SOP — model correctly flags `in_scope: false` |
| `escalation.md` | Complaint — both Layer 1 keyword and Layer 2 model signal fire |
| `qualification.md` | Full qualification flow with structured extraction |
| `summary.md` | End-to-end summary generation from a complete session |

These transcripts serve as regression evidence: if the prompts or logic change, they can be re-generated and diffed against previous runs.

## Honest Tradeoffs and Limitations
- **Keyword Fragility (Layer 1):** Deterministic rules are brittle. "I am not angry" contains the keyword "angry" and might trigger a false positive escalation if the regex isn't careful.
- **Context Window:** Injecting the entire SOP into the system prompt on every turn is feasible for a small clinic SOP. If the clinic's SOP grows to thousands of pages, this architecture will become too slow and expensive, requiring a vector database and RAG approach.
- **Latency:** Calling the model on every turn, especially for the multi-step JSON generation and summary generation, introduces latency compared to a simple decision-tree chatbot.
- **Tone Drift:** Even with strong persona prompting, models can occasionally drift into overly verbose or generic customer service platitudes if not tightly reigned in.
