# Prompt Versioning & Rollback Strategy

Managing LLM prompts is similar to managing code. Small changes in wording can drastically alter model behavior, hallucination rates, and explainability. This strategy defines how we evolve our recommendation prompts safely.

## 1. Versioning
Prompts should be stored in source control (like our current implementation in `llm_groq.py`) and treated as immutable versions.
- **Current Prompt:** Version `1.1.0` (Includes `additional_preferences` strict constraint).
- When a prompt is updated, it should be tested against the Phase 6 evaluation dataset before merging to `main`.

## 2. A/B Testing & Rollouts (Future Implementation)
In the future, the orchestrator should support passing a `prompt_version` flag. 
- 90% of traffic receives `v1.1.0`
- 10% of traffic receives `v1.2.0-experimental`

## 3. Rollback Plan
If a new prompt deployment causes an increase in "Not Helpful" feedback via the `/feedback` endpoint:
1. Revert the commit in `llm_groq.py` that changed the prompt.
2. Push to GitHub. Railway will auto-deploy the previous, stable version within 2 minutes.

## 4. Feedback Loop
The `/feedback/stats` endpoint currently tracks Helpful vs Not Helpful metrics.
- Monitor this weekly. If the "Helpful" percentage drops below 80%, investigate the latest query logs to see if the LLM is hallucinating or ignoring constraints.
