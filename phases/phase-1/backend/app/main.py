from fastapi import FastAPI, HTTPException, Query
from typing import Optional

from .config import settings
from .schemas import CatalogStats, Restaurant
from .services.catalog import CatalogNotFoundError, compute_stats, filter_restaurants, load_catalog

app = FastAPI(
    title=settings.app_name,
    version="1.0.0-phase1",
    description="Phase 1 catalog service with ingestion-backed normalized restaurant data.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "phase": "phase-1",
        "environment": settings.app_env,
    }


@app.get("/catalog/restaurants", response_model=list[Restaurant])
def get_restaurants(
    city: Optional[str] = Query(default=None),
    cuisine: Optional[str] = Query(default=None),
    min_rating: Optional[float] = Query(default=None, ge=0.0, le=5.0),
    max_cost_for_two: Optional[float] = Query(default=None, ge=0.0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Restaurant]:
    try:
        restaurants = load_catalog(str(settings.catalog_path))
    except CatalogNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{error}. Run ingestion first: "
                "python phases/phase-1/backend/scripts/ingest_zomato.py"
            ),
        ) from error

    return filter_restaurants(
        restaurants,
        city=city,
        cuisine=cuisine,
        min_rating=min_rating,
        max_cost_for_two=max_cost_for_two,
        limit=limit,
    )


@app.get("/catalog/stats", response_model=CatalogStats)
def get_catalog_stats() -> CatalogStats:
    try:
        restaurants = load_catalog(str(settings.catalog_path))
    except CatalogNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{error}. Run ingestion first: "
                "python phases/phase-1/backend/scripts/ingest_zomato.py"
            ),
        ) from error

    return compute_stats(restaurants)
