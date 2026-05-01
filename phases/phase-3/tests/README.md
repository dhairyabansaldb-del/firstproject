# Phase 3 Tests

Recommended tests:
- request validation (`budget`, `min_rating`, `limit`)
- strict filtering happy path
- fallback behavior when strict filters return zero candidates
- deterministic ordering by rating/votes/cost
- missing catalog file returns `503`
