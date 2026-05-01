# Phase 1: Data Pipeline and Catalog Service (Isolated)

This folder contains only Phase 1 implementation so work remains separated by phase.

## Scope in this phase
- One-time ingestion script for the Zomato dataset from Hugging Face
- Data preprocessing and canonical normalization
- Local catalog storage in JSON
- Queryable backend API for catalog reads

## Structure
- `backend/` - FastAPI service and ingestion pipeline
- `tests/` - placeholder for phase-scoped tests

## Setup
1. Create virtual environment and activate it.
2. Install dependencies:
   - `pip install -r phases/phase-1/backend/requirements.txt`
3. Optional: copy `phases/phase-1/.env.example` to `phases/phase-1/.env`.

## Ingest dataset
From project root:
- `python phases/phase-1/backend/scripts/ingest_zomato.py`

Output file:
- `phases/phase-1/backend/data/restaurants.normalized.json`

## Run Phase 1 API
From project root:
- `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8100 --app-dir phases/phase-1/backend`

Alternative:
- `python phases/phase-1/backend/run.py`

## Available endpoints
- `GET /health`
- `GET /catalog/restaurants` (supports filters)
- `GET /catalog/stats`

## Notes
- This phase does not include LLM ranking yet.
- This implementation is built to address key ingestion/filtering edge cases from `docs/edge-cases.md`.
