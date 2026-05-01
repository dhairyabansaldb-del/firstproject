from fastapi import FastAPI, HTTPException

from .config import settings
from .schemas import RecommendationsRequest, RecommendationsResponse
from .services.catalog import CatalogLoadError, load_catalog
from .services.filtering import build_candidates
from .services.orchestrator import generate_ranked_recommendations

app = FastAPI(
    title=settings.app_name,
    version="4.0.0-phase4",
    description="Architecture Phase 4: Groq LLM ranking and explanation service.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "phase": "phase-4",
        "environment": settings.app_env,
    }


@app.post("/recommendations", response_model=RecommendationsResponse)
def recommendations(request: RecommendationsRequest) -> RecommendationsResponse:
    try:
        catalog = load_catalog(str(settings.catalog_path))
    except CatalogLoadError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{error}. Generate catalog with: "
                "python phases/phase-2/backend/scripts/ingest_zomato.py"
            ),
        ) from error

    candidates = build_candidates(catalog=catalog, request=request)
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail=(
                "No candidates found for the provided preferences. "
                "Try relaxing cuisine, rating, or budget constraints."
            ),
        )

    ranked, used_fallback, fallback_reason = generate_ranked_recommendations(
        request=request, candidates=candidates
    )

    return RecommendationsResponse(
        request=request,
        total_candidates_considered=len(candidates),
        used_fallback=used_fallback,
        fallback_reason=fallback_reason,
        recommendations=ranked,
        candidate_lookup=candidates,
    )
