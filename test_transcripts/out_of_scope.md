# Out Of Scope Transcript

```text
2026-05-24 02:03:27 [INFO] Closira agent starting...

=== Bloom Aesthetics Clinic - FAQ Agent ===
Type "done" to finish FAQ and move to qualification.

You: Do you offer haircuts?
2026-05-24 02:03:27 [INFO] FAQ Service - Request received.
2026-05-24 02:03:29 [INFO] FAQ Service - Parsed response metadata: in_scope=False, requires_escalation=True
2026-05-24 02:03:29 [INFO] Escalation Service - ESCALATE | Triggered by: layer2 | Layer 2: model_out_of_scope

Agent: I'm sorry, but we don't offer haircuts at Bloom Aesthetics Clinic. I'm escalating your message to a human teammate who can provide more information on the aesthetic treatments we do offer.
  [!] Escalation: Layer 2: model_out_of_scope

You: done

=== Qualification ===
Before we wrap up, a few quick questions:

2026-05-24 02:03:29 [INFO] Qualification Service - Starting qualification flow.

  Q1: What type of service are you interested in? (e.g., Botox, Fillers, Consultation, other)
  > 
  Q2: How many people will be attending, or is this just for yourself?
  > 
  Q3: Have you had any aesthetic treatments before, and if so, where?
  > 
2026-05-24 02:03:29 [INFO] Qualification Service - Collected answers: {'service_interest': None, 'party_size': None, 'prior_experience': None}

--- Qualification Collected ---
{
  "service_interest": null,
  "party_size": null,
  "prior_experience": null
}
-------------------------------

=== Session Summary ===
2026-05-24 02:03:29 [INFO] Summary Service - Generating session summary.
2026-05-24 02:03:31 [INFO] Summary Service - Summary generated successfully.
{
  "customer_intent": "The customer asked if haircuts are offered.",
  "details_collected": {
    "service_interest": null,
    "party_size": null,
    "prior_experience": null
  },
  "sop_gaps": [
    "Haircuts are not offered, requested details on services."
  ],
  "recommended_next_action": "Follow up to clarify that the clinic specializes in Botox and Fillers, and does not offer haircuts."
}
=======================

2026-05-24 02:03:31 [INFO] Closira agent session complete.
```
