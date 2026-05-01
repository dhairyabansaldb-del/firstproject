# Phase 4: LLM Ranking and Explanation Layer (Groq)

This folder contains an isolated implementation of Architecture Phase 4.

## Scope
- Accept typed user preferences
- Build filtered shortlist candidates
- Send structured prompt to **Groq** LLM for ranking + explanation
- Enforce strict JSON output contract
- Fallback to deterministic ranking if LLM fails validation
- Final endpoint: `POST /recommendations`

## Setup
1. Install dependencies:
   - `pip install -r phases/phase-4/backend/requirements.txt`
2. Copy env template:
   - `copy phases\\phase-4\\.env.example phases\\phase-4\\.env`
3. Set `GROQ_API_KEY` in `.env`

## Run API
- `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8400 --app-dir phases/phase-4/backend`

## Endpoints
- `GET /health`
- `POST /recommendations`

## Notes
- Catalog source defaults to Phase 2 normalized dataset.
- If Groq is unavailable or returns invalid output, service returns deterministic fallback rankings.
