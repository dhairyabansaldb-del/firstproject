# Phase 0 Implementation (Foundation Baseline)

This document captures what has been implemented as the project baseline before feature phases.

## Implemented
- Backend scaffold using FastAPI in `backend/`
- Health-check endpoint: `GET /health`
- Config baseline via environment variables (`.env.example`)
- Frontend shell in `frontend/` that calls backend health endpoint
- Core project directories created: `data/`, `prompts/`, `tests/`
- Updated setup/run instructions in `README.md`

## Verification Steps
1. Create and activate virtual environment.
2. Install backend dependencies from `backend/requirements.txt`.
3. Run backend:
   - `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
4. Run frontend:
   - `cd frontend`
   - `python -m http.server 5500`
5. Open `http://127.0.0.1:5500` and click **Check Health**.

Expected output includes:
- `status: ok`
- service name
- environment value
