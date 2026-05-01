# AI Restaurant Recommendation Service

Phase 0 foundation scaffold for the Zomato-inspired AI restaurant recommendation system.

## Project Structure
- `backend/` - FastAPI backend service
- `frontend/` - lightweight web UI shell
- `data/` - data assets and local snapshots
- `prompts/` - prompt templates for LLM ranking
- `tests/` - test suite scaffold
- `docs/` - product and architecture documentation
- `phases/` - isolated implementation folders per phase

## Local Setup
1. Create backend virtual environment and install dependencies:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
   - `pip install -r backend/requirements.txt`
2. Copy `.env.example` to `.env` and adjust values if needed.

## Run Backend
From project root:
- `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`

## Run Frontend
From `frontend/`:
- `python -m http.server 5500`

Then open [http://127.0.0.1:5500](http://127.0.0.1:5500) and click **Check Health**.

## Phase 0 Outcome
- Backend service bootstrapped with `GET /health`
- Frontend shell can call backend
- Baseline folder structure created for upcoming phases
