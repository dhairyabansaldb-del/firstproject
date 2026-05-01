from fastapi import FastAPI, HTTPException

from .config import settings
from .schemas import (
    RecommendationPreviewRequest,
    RecommendationPreviewResponse,
    RestaurantCandidate,
)
from .services.catalog import CatalogLoadError, load_catalog
from .services.filtering import run_filtering_with_fallbacks

app = FastAPI(
    title=settings.app_name,
    version="3.0.0-phase3",
    description="Architecture Phase 3: typed preference intake and deterministic filtering.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "phase": "phase-3",
        "environment": settings.app_env,
    }


@app.post("/recommendations/preview", response_model=RecommendationPreviewResponse)
def recommendation_preview(
    request: RecommendationPreviewRequest,
) -> RecommendationPreviewResponse:
    try:
        catalog = load_catalog(str(settings.catalog_path))
    except CatalogLoadError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{error}. Generate catalog first with phase 2 ingestion: "
                "python phases/phase-2/backend/scripts/ingest_zomato.py"
            ),
        ) from error

    filtering_result = run_filtering_with_fallbacks(catalog=catalog, request=request)

    # Deterministic order: rating desc, votes desc, cost asc
    ordered = sorted(
        filtering_result.matches,
        key=lambda row: (
            -(float(row.get("rating") or 0.0)),
            -(int(row.get("votes") or 0)),
            float(row.get("average_cost_for_two") or 999999),
        ),
    )
    ordered = ordered[: request.limit]

    candidates = [
        RestaurantCandidate(
            restaurant_id=str(row.get("restaurant_id", "")),
            name=str(row.get("name", "")),
            location=str(row.get("location", "")),
            city=str(row.get("city", "")),
            cuisines=[str(c) for c in row.get("cuisines", [])],
            average_cost_for_two=(
                float(row["average_cost_for_two"])
                if row.get("average_cost_for_two") is not None
                else None
            ),
            currency=str(row["currency"]) if row.get("currency") else None,
            rating=float(row["rating"]) if row.get("rating") is not None else None,
            votes=int(row["votes"]) if row.get("votes") is not None else None,
        )
        for row in ordered
    ]

    return RecommendationPreviewResponse(
        request=request,
        matched_count=len(candidates),
        used_fallback=len(filtering_result.relaxations) > 0,
        applied_relaxations=filtering_result.relaxations,
        candidates=candidates,
    )
