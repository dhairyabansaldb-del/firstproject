#!/bin/bash
# Dataset is now committed directly to the repo to prevent OOM errors on Railway startup

# Start Phase 4 internally (Core Recommendation API)
python -m uvicorn phases.phase-4.backend.app.main:app --host 127.0.0.1 --port 8401 &

# Start Phase 5 publicly (Proxy and Orchestration API)
# Railway provides the public PORT dynamically
PORT="${PORT:-8500}"
python -m uvicorn phases.phase-5.backend.app.main:app --host 0.0.0.0 --port $PORT
