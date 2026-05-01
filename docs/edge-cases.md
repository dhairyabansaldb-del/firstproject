# Detailed Edge Cases: AI-Powered Restaurant Recommendation System

## How to Use This Document
- Each edge case includes: **Scenario**, **Risk**, **Expected System Behavior**, and **Mitigation/Implementation Notes**.
- Use this as both a build-time checklist and a QA test-plan source.
- Priority tags:
  - **P0** = must handle before release
  - **P1** = should handle in MVP
  - **P2** = nice to handle soon after MVP

## 1) Data Ingestion and Preprocessing Edge Cases

### EC-DATA-001 (P0): Dataset source unavailable
**Scenario:** Hugging Face dataset URL is down, rate-limited, or unreachable.  
**Risk:** Pipeline fails; app cannot refresh data.  
**Expected behavior:** Ingestion fails gracefully with clear error logs and non-zero exit status; previous valid dataset remains usable.  
**Mitigation:** Retry with backoff, timeout safeguards, local cached snapshot fallback.

### EC-DATA-002 (P0): Schema drift in source data
**Scenario:** Column names/types change (for example `avg_cost` renamed).  
**Risk:** Silent corruption or runtime failures.  
**Expected behavior:** Schema validation fails fast with actionable diagnostics.  
**Mitigation:** Versioned schema contract and validation checks before transformation.

### EC-DATA-003 (P0): Critical fields missing
**Scenario:** Restaurant rows missing `name`, `location`, `rating`, or `cost`.  
**Risk:** Invalid recommendations or crashes in filtering/ranking.  
**Expected behavior:** Invalid rows are dropped or imputed by explicit rules; counts are reported.  
**Mitigation:** Required-field validator + ingestion quality report.

### EC-DATA-004 (P1): Duplicate restaurants across rows
**Scenario:** Same restaurant appears multiple times with slight text differences.  
**Risk:** Duplicated recommendation cards, skewed ranking.  
**Expected behavior:** Deduplicate records using deterministic key strategy.  
**Mitigation:** Normalize names/locations, fuzzy dedupe threshold + audit list.

### EC-DATA-005 (P1): Inconsistent cuisine formatting
**Scenario:** `North Indian`, `north-indian`, `NorthIndian`, multi-cuisine delimiters differ.  
**Risk:** Incorrect filtering and low recall.  
**Expected behavior:** Cuisine normalization to canonical tokens.  
**Mitigation:** Controlled vocabulary + mapping table.

### EC-DATA-006 (P1): Rating out-of-range or malformed
**Scenario:** Ratings are null, strings (`"4/5"`), or out of bounds.  
**Risk:** Filter errors and invalid user trust signals.  
**Expected behavior:** Parse, normalize, clip/reject invalid values by policy.  
**Mitigation:** Strict numeric parser and range validation.

### EC-DATA-007 (P2): Currency/cost scale inconsistency
**Scenario:** Cost fields mixed (per person vs for two; INR vs other currency).  
**Risk:** Wrong budget matching.  
**Expected behavior:** Convert to one canonical cost basis before filtering.  
**Mitigation:** Metadata-aware conversion and unit normalization rules.

### EC-DATA-008 (P2): Very large dataset ingestion time
**Scenario:** Source grows significantly and ingestion exceeds expected runtime.  
**Risk:** Slow deployments and stale catalog updates.  
**Expected behavior:** Pipeline remains stable and measurable with progress logs.  
**Mitigation:** Batch processing, incremental updates, indexing, and caching.

## 2) Preference Intake and Validation Edge Cases

### EC-INPUT-001 (P0): Empty request payload
**Scenario:** User submits no preferences.  
**Risk:** Undefined behavior or meaningless recommendations.  
**Expected behavior:** Return validation error with required fields guidance (or apply documented defaults).  
**Mitigation:** Input schema validation at API boundary.

### EC-INPUT-002 (P0): Invalid location
**Scenario:** Misspelled city or unsupported locality.  
**Risk:** Zero candidates despite user intent.  
**Expected behavior:** Offer close matches/suggestions or request correction.  
**Mitigation:** Fuzzy location matching + known-location dictionary.

### EC-INPUT-003 (P0): Invalid budget label/value
**Scenario:** Budget input outside `low|medium|high` (or negative numeric budget).  
**Risk:** Filter misbehavior or no results.  
**Expected behavior:** Reject with clear validation message and accepted values.  
**Mitigation:** Enum validation and normalization map.

### EC-INPUT-004 (P0): Minimum rating out of range
**Scenario:** User provides `min_rating = 6` or negative rating.  
**Risk:** Empty results or logical errors.  
**Expected behavior:** Validation error with accepted range (for example 0-5).  
**Mitigation:** Numeric constraints in request schema.

### EC-INPUT-005 (P1): Contradictory constraints
**Scenario:** Low budget + luxury cuisine + rating >= 4.9 in sparse city.  
**Risk:** Frequent no-result outcomes.  
**Expected behavior:** Explain conflict and return nearest relaxed alternatives.  
**Mitigation:** Constraint-relaxation strategy with explicit fallback order.

### EC-INPUT-006 (P1): Unsupported cuisine values
**Scenario:** User asks for unknown cuisine taxonomy.  
**Risk:** Hard zero candidates.  
**Expected behavior:** Suggest nearest supported cuisines and continue optionally.  
**Mitigation:** Cuisine synonym map + similarity lookup.

### EC-INPUT-007 (P2): Adversarial/free-text prompt injection in preferences
**Scenario:** Optional preference contains instructions targeting system prompt.  
**Risk:** LLM behavior manipulation.  
**Expected behavior:** Treat user input as data, not instructions; sanitize before prompt assembly.  
**Mitigation:** Prompt isolation delimiters + allowlist/escaping rules.

## 3) Deterministic Filtering Edge Cases

### EC-FILTER-001 (P0): Zero candidates after strict filtering
**Scenario:** Filter output is empty.  
**Risk:** Dead-end user experience.  
**Expected behavior:** Return no-match explanation + progressively relaxed alternatives.  
**Mitigation:** Multi-step fallback (rating -> budget -> cuisine expansion) with user-visible notes.

### EC-FILTER-002 (P0): Too many candidates (prompt overflow risk)
**Scenario:** Dense city + broad preferences produce thousands of candidates.  
**Risk:** LLM context overflow, high latency/cost.  
**Expected behavior:** Pre-rank and cap shortlist before LLM call.  
**Mitigation:** Deterministic pre-scoring and top-N candidate limit.

### EC-FILTER-003 (P1): Tie-heavy candidate set
**Scenario:** Multiple restaurants share identical ratings/cost bands.  
**Risk:** Unstable ordering across requests.  
**Expected behavior:** Deterministic tie-breakers produce consistent order.  
**Mitigation:** Stable sort with secondary keys (review count, distance, name).

### EC-FILTER-004 (P1): Location granularity mismatch
**Scenario:** Dataset has neighborhood-level locations; user provides city-level location.  
**Risk:** False negatives in filtering.  
**Expected behavior:** Hierarchical location matching and expansion.  
**Mitigation:** City-neighborhood mapping table.

### EC-FILTER-005 (P2): Repeated exact query flooding
**Scenario:** Same user/request sent many times quickly.  
**Risk:** API load spikes and LLM cost waste.  
**Expected behavior:** Idempotent cache hit where possible.  
**Mitigation:** Query fingerprint cache with short TTL.

## 4) LLM Ranking and Explanation Edge Cases

### EC-LLM-001 (P0): LLM API timeout or service outage
**Scenario:** Upstream LLM is unavailable or slow.  
**Risk:** Failed recommendations and poor UX.  
**Expected behavior:** Return deterministic fallback ranking with transparent message.  
**Mitigation:** Timeout + retry + circuit breaker + fallback engine.

### EC-LLM-002 (P0): Non-JSON or malformed response
**Scenario:** Model returns prose instead of contract schema.  
**Risk:** Parser failures and API errors.  
**Expected behavior:** Attempt one structured retry; otherwise fallback response path.  
**Mitigation:** Strict output schema validation and robust parser.

### EC-LLM-003 (P0): Hallucinated restaurants not in candidate list
**Scenario:** LLM invents names or attributes.  
**Risk:** Trust and correctness failure.  
**Expected behavior:** Reject any recommendation not in candidate IDs.  
**Mitigation:** Candidate-ID constrained prompting + post-validation.

### EC-LLM-004 (P0): Explanation contradicts user constraints
**Scenario:** Recommends expensive place for low-budget user without rationale.  
**Risk:** Perceived irrelevance.  
**Expected behavior:** Consistency checks between recommendation and constraints.  
**Mitigation:** Rule-based validator and explanation quality guardrails.

### EC-LLM-005 (P1): Unsafe or biased language in explanation
**Scenario:** Response includes stereotyping or inappropriate content.  
**Risk:** Safety/compliance issue.  
**Expected behavior:** Block/redact unsafe content and return safe fallback copy.  
**Mitigation:** Safety moderation layer and template-driven explanations for fallback.

### EC-LLM-006 (P1): Latency spikes under peak traffic
**Scenario:** High concurrent requests increase model response time.  
**Risk:** User drop-offs.  
**Expected behavior:** Maintain bounded response times with graceful degradation.  
**Mitigation:** Async queueing, time budget cutoff, deterministic fast path.

### EC-LLM-007 (P2): Model version drift changes ranking style
**Scenario:** Provider model update alters behavior unexpectedly.  
**Risk:** Inconsistent user experience.  
**Expected behavior:** Stable behavior via version pinning and regression checks.  
**Mitigation:** Versioned prompts + offline evaluation before upgrade.

## 5) API and Backend Edge Cases

### EC-API-001 (P0): Invalid JSON or wrong content-type
**Scenario:** Client sends malformed request body.  
**Risk:** Unhandled exceptions.  
**Expected behavior:** Return `400` with structured error object.  
**Mitigation:** Global exception handler and request validation middleware.

### EC-API-002 (P0): Backend startup without required env vars
**Scenario:** Missing API key or configuration.  
**Risk:** Runtime failures in production.  
**Expected behavior:** Fail fast on startup with explicit missing variable names.  
**Mitigation:** Config validation at boot.

### EC-API-003 (P1): Partial downstream failure
**Scenario:** Catalog service is up but LLM service is down (or vice versa).  
**Risk:** End-to-end flow breaks.  
**Expected behavior:** Degraded mode still returns useful output if possible.  
**Mitigation:** Service-level fallbacks and resilient orchestration.

### EC-API-004 (P1): Cache poisoning or stale cache
**Scenario:** Old recommendations served after data refresh.  
**Risk:** Incorrect or outdated results.  
**Expected behavior:** Cache invalidates on catalog version change.  
**Mitigation:** Cache key includes dataset version + prompt version.

### EC-API-005 (P2): Unbounded request payload size
**Scenario:** Extremely long optional preference text.  
**Risk:** Memory/performance issues and prompt overflow.  
**Expected behavior:** Reject or truncate based on strict limits.  
**Mitigation:** Payload size caps and text length validators.

## 6) Frontend and UX Edge Cases

### EC-UI-001 (P0): Form submission with missing required fields
**Scenario:** User submits incomplete form.  
**Risk:** Backend errors and user confusion.  
**Expected behavior:** Inline validation errors before API call.  
**Mitigation:** Client-side schema validation mirroring backend rules.

### EC-UI-002 (P0): No-result response handling
**Scenario:** API returns no candidates even after fallback.  
**Risk:** User dead-end.  
**Expected behavior:** Show clear no-result state with actionable suggestions.  
**Mitigation:** UX copy + one-click relax filters action.

### EC-UI-003 (P1): Slow response and user double-submits
**Scenario:** User clicks submit multiple times.  
**Risk:** Duplicate API calls and inconsistent UI state.  
**Expected behavior:** Disable submit while in-flight and show spinner/progress.  
**Mitigation:** Request locking/debouncing.

### EC-UI-004 (P1): Network interruption during request
**Scenario:** Client disconnects or flaky internet.  
**Risk:** Broken session and frustration.  
**Expected behavior:** Retry option with preserved form state.  
**Mitigation:** Error boundary + local state persistence.

### EC-UI-005 (P2): Recommendation card data missing fields
**Scenario:** One recommendation has null cost/cuisine after pipeline drift.  
**Risk:** Broken layout or empty labels.  
**Expected behavior:** Show graceful placeholders and avoid layout breaks.  
**Mitigation:** Defensive rendering and UI fallback tokens.

## 7) Observability, Evaluation, and Operations Edge Cases

### EC-OPS-001 (P0): No correlation IDs across services
**Scenario:** Failures occur but cannot trace request path.  
**Risk:** Long incident resolution times.  
**Expected behavior:** Every request gets a trace/correlation ID propagated end-to-end.  
**Mitigation:** Middleware-based request ID injection and logging standards.

### EC-OPS-002 (P1): Metrics blind spots
**Scenario:** Success rate appears high but explanation quality is poor.  
**Risk:** False confidence in system health.  
**Expected behavior:** Track quality metrics, not only uptime/latency.  
**Mitigation:** Add relevance score proxies and user feedback metrics.

### EC-OPS-003 (P1): Evaluation set becomes stale
**Scenario:** Offline benchmark no longer reflects real user queries.  
**Risk:** Regressions go unnoticed.  
**Expected behavior:** Periodic refresh of evaluation dataset.  
**Mitigation:** Scheduled eval curation from anonymized real queries.

### EC-OPS-004 (P2): Cost overrun from LLM usage
**Scenario:** Prompt sizes or request volume spike unexpectedly.  
**Risk:** Budget impact.  
**Expected behavior:** Cost guards trigger alerts and degrade gracefully.  
**Mitigation:** Token budgeting, per-request limits, and usage alerts.

## 8) Security and Privacy Edge Cases

### EC-SEC-001 (P0): API key leakage via logs
**Scenario:** Sensitive env vars accidentally logged.  
**Risk:** Credential compromise.  
**Expected behavior:** Secrets are redacted in logs and errors.  
**Mitigation:** Secret masking middleware + secure logging policy.

### EC-SEC-002 (P0): Prompt injection through user preferences
**Scenario:** User attempts to override system instructions via optional text.  
**Risk:** Policy bypass and unsafe outputs.  
**Expected behavior:** Input treated as untrusted text; model constrained to candidate data.  
**Mitigation:** Input sanitization, strong system prompts, output validation.

### EC-SEC-003 (P1): Excessive data exposure in API response
**Scenario:** Internal metadata or raw dataset fields exposed to client.  
**Risk:** Privacy/compliance concerns.  
**Expected behavior:** Response only includes approved public fields.  
**Mitigation:** Response DTO allowlist and serialization guard.

### EC-SEC-004 (P2): Abuse via automated scraping
**Scenario:** Bots hammer recommendations endpoint.  
**Risk:** Service degradation and higher infra/LLM cost.  
**Expected behavior:** Detect and throttle abusive patterns.  
**Mitigation:** Rate limits, API keys (if needed), and anomaly detection.

## 9) Cross-Cutting Regression Scenarios (Must Test Before Release)
- **RG-001 (P0):** Known valid query returns at least 5 relevant recommendations with explanations.
- **RG-002 (P0):** No-match query returns graceful fallback suggestions (not a 500).
- **RG-003 (P0):** LLM failure path still returns deterministic ranked output.
- **RG-004 (P0):** All recommendation items belong to filtered candidate set (no hallucinations).
- **RG-005 (P1):** Repeated same query hits cache and reduces latency.
- **RG-006 (P1):** Input validation errors are consistent between frontend and backend.
- **RG-007 (P1):** Prompt/output schema changes do not break parsing.

## 10) Suggested Next Testing Artifacts
- Convert all **P0** and **P1** cases into executable test cases (`unit`, `integration`, `e2e`).
- Create a `golden_queries.json` file for stable recommendation regression checks.
- Add CI gates for:
  - schema validation
  - hallucination prevention checks
  - fallback-path correctness
