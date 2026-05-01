# Phase 5: User Experience and Result Presentation (Isolated)

This folder contains an isolated implementation of Architecture Phase 5.

## Purpose
Deliver clear and trustworthy recommendations to users with an interactive UI.

## Scope
- Interactive preference form with location, budget, cuisine, rating inputs
- Loading state during recommendation processing
- Recommendation result cards with explanations
- User feedback capture (helpful/not helpful)
- Explainability-first card layout

## Structure
- `frontend/` - Interactive web UI with preference form and result cards
- `backend/` - API service that calls Phase 4 recommendation engine
- `tests/` - Placeholder for phase-scoped tests

## Setup
1. Install dependencies:
   - `pip install -r phases/phase-5/backend/requirements.txt`
2. Optional: copy `phases/phase-5/.env.example` to `phases/phase-5/.env`
3. Ensure Phase 4 service is running on port 8401

## Run Frontend
From project root:
- `cd phases/phase-5/frontend && python -m http.server 5500`

## Run Backend API
From project root:
- `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8500 --app-dir phases/phase-5/backend`

## Endpoints
- `GET /health`
- `POST /recommendations` (proxies to Phase 4 service)
- `POST /feedback` (captures user feedback)

## Features
- **Preference Form**: Location dropdown, budget selector, cuisine multi-select, rating slider
- **Loading States**: Spinner and progress indicators during API calls
- **Result Cards**: Restaurant details with AI explanations, ratings, cost, cuisines
- **Feedback System**: Helpful/Not helpful buttons with optional comments
- **Responsive Design**: Works on desktop and mobile devices

## Notes
- This phase focuses on user experience and presentation
- Uses Phase 4 backend for actual recommendation logic
- Includes error handling and retry mechanisms
- Implements explainability-first design principles
