# Phase 3: Preference Intake and Deterministic Filtering (Isolated)

This folder contains an isolated implementation of Architecture Phase 3.

## Scope
- Strongly-typed user preference intake
- Input normalization and validation
- Deterministic candidate filtering
- Graceful fallback behavior when strict filters return no matches
- `POST /recommendations/preview` endpoint (no LLM yet)

## Setup
1. Install dependencies:
   - `pip install -r phases/phase-3/backend/requirements.txt`
2. Optional: copy `phases/phase-3/.env.example` to `phases/phase-3/.env`
3. Ensure Phase 2 catalog exists, or point `CATALOG_FILE` to your normalized data.

## Run API
- `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8300 --app-dir phases/phase-3/backend`

## Endpoints
- `GET /health`
- `POST /recommendations/preview`

## Example Request
```json
{
  "location": "Banashankari",
  "budget": "medium",
  "cuisine": "North Indian",
  "min_rating": 4.0,
  "additional_preferences": ["family-friendly", "quick service"],
  "limit": 10
}
```
