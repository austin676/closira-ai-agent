# Summary Transcript

```text
2026-05-24 02:06:18 [INFO] Closira agent starting...

=== Bloom Aesthetics Clinic - FAQ Agent ===
Type "done" to finish FAQ and move to qualification.

You: How much is botox?
2026-05-24 02:06:18 [INFO] FAQ Service - Request received.
2026-05-24 02:06:21 [INFO] FAQ Service - Parsed response metadata: in_scope=True, requires_escalation=False
2026-05-24 02:06:21 [INFO] Escalation Service - No escalation needed.

Agent: Botox treatments at Bloom Aesthetics Clinic start from £200.

You: done

=== Qualification ===
Before we wrap up, a few quick questions:

2026-05-24 02:06:21 [INFO] Qualification Service - Starting qualification flow.

  Q1: What type of service are you interested in? (e.g., Botox, Fillers, Consultation, other)
  > Botox
  Q2: How many people will be attending, or is this just for yourself?
  > Just me
  Q3: Have you had any aesthetic treatments before, and if so, where?
  > No
2026-05-24 02:06:21 [INFO] Qualification Service - Collected answers: {'service_interest': 'Botox', 'party_size': 'Just me', 'prior_experience': 'No'}

--- Qualification Collected ---
{
  "service_interest": "Botox",
  "party_size": "Just me",
  "prior_experience": "No"
}
-------------------------------

=== Session Summary ===
2026-05-24 02:06:21 [INFO] Summary Service - Generating session summary.
2026-05-24 02:06:23 [INFO] Summary Service - Summary generated successfully.
{
  "customer_intent": "The customer asked about the starting price for Botox.",
  "details_collected": {
    "service_interest": "Botox",
    "party_size": "Just me",
    "prior_experience": "No"
  },
  "sop_gaps": [],
  "recommended_next_action": "Follow up to confirm if they'd like to book a free consultation for Botox."
}
=======================

2026-05-24 02:06:23 [INFO] Closira agent session complete.
```
