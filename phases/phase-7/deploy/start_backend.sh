#!/bin/bash
# Fetch and build the Zomato data catalog on the Railway server
python phases/phase-1/backend/scripts/ingest_zomato.py

# Start Phase 4 internally (Core Recommendation API)
python -m uvicorn phases.phase-4.backend.app.main:app --host 127.0.0.1 --port 8401 &

# Start Phase 5 publicly (Proxy and Orchestration API)
# Railway provides the public PORT dynamically
PORT="${PORT:-8500}"
python -m uvicorn phases.phase-5.backend.app.main:app --host 0.0.0.0 --port $PORT
