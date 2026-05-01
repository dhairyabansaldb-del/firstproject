# Phase 2: Data Pipeline and Restaurant Catalog Service (Isolated)

This folder contains an isolated implementation of Architecture Phase 2.

## Scope
- One-time ingestion script for Hugging Face Zomato dataset
- Preprocessing and canonical normalization
- Local catalog storage (JSON)
- Catalog API for filtered reads
- Ingestion quality report

## Setup
1. Install dependencies:
   - `pip install -r phases/phase-2/backend/requirements.txt`
2. Optional: copy `phases/phase-2/.env.example` to `phases/phase-2/.env`

## Run ingestion
- `python phases/phase-2/backend/scripts/ingest_zomato.py`

Outputs:
- `phases/phase-2/backend/data/restaurants.normalized.json`
- `phases/phase-2/backend/data/ingestion.report.json`

## Run API
- `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8200 --app-dir phases/phase-2/backend`

## Endpoints
- `GET /health`
- `GET /catalog/restaurants`
- `GET /catalog/stats`
- `GET /catalog/quality-report`
