from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from .config import settings
from .schemas import CatalogStats, IngestionReport, Restaurant
from .services.catalog import (
    CatalogFileError,
    compute_stats,
    filter_catalog,
    load_catalog,
    load_quality_report,
)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0-phase2",
    description="Architecture Phase 2: ingestion-backed restaurant catalog service.",
)


def _ingestion_hint() -> str:
    return "Run: python phases/phase-2/backend/scripts/ingest_zomato.py"


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "phase": "phase-2",
        "environment": settings.app_env,
    }


@app.get("/catalog/restaurants", response_model=list[Restaurant])
def get_catalog_restaurants(
    city: Optional[str] = Query(default=None),
    cuisine: Optional[str] = Query(default=None),
    min_rating: Optional[float] = Query(default=None, ge=0.0, le=5.0),
    max_cost_for_two: Optional[float] = Query(default=None, ge=0.0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Restaurant]:
    try:
        restaurants = load_catalog(str(settings.catalog_path))
    except CatalogFileError as error:
        raise HTTPException(
            status_code=503, detail=f"{error}. {_ingestion_hint()}"
        ) from error
    return filter_catalog(
        restaurants=restaurants,
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
    except CatalogFileError as error:
        raise HTTPException(
            status_code=503, detail=f"{error}. {_ingestion_hint()}"
        ) from error
    return compute_stats(restaurants)


@app.get("/catalog/quality-report", response_model=IngestionReport)
def get_ingestion_quality_report() -> IngestionReport:
    try:
        return load_quality_report(str(settings.report_path))
    except CatalogFileError as error:
        raise HTTPException(
            status_code=503, detail=f"{error}. {_ingestion_hint()}"
        ) from error
