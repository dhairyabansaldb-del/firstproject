# Phase 4 Tests

Recommended coverage:
- request validation for `/recommendations`
- Groq success path with valid JSON output
- invalid Groq output -> deterministic fallback
- unknown restaurant IDs from model -> fallback
- no candidate scenario -> `404`
