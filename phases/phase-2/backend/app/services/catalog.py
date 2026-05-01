import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ..schemas import CatalogStats, IngestionReport, Restaurant


class CatalogFileError(FileNotFoundError):
    pass


@lru_cache(maxsize=1)
def load_catalog(catalog_path: str) -> list[Restaurant]:
    path = Path(catalog_path)
    if not path.exists():
        raise CatalogFileError(f"Catalog file not found at: {path}")
    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    return [Restaurant.model_validate(item) for item in raw]


def filter_catalog(
    restaurants: list[Restaurant],
    city: Optional[str] = None,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_cost_for_two: Optional[float] = None,
    limit: int = 20,
) -> list[Restaurant]:
    results = restaurants
    if city:
        needle = city.strip().lower()
        results = [r for r in results if r.city.lower() == needle]
    if cuisine:
        needle = cuisine.strip().lower()
        results = [r for r in results if any(needle == c.lower() for c in r.cuisines)]
    if min_rating is not None:
        results = [r for r in results if r.rating is not None and r.rating >= min_rating]
    if max_cost_for_two is not None:
        results = [
            r
            for r in results
            if r.average_cost_for_two is not None
            and r.average_cost_for_two <= max_cost_for_two
        ]
    return results[:limit]


def compute_stats(restaurants: list[Restaurant]) -> CatalogStats:
    cities = {r.city for r in restaurants}
    cuisines = set()
    for restaurant in restaurants:
        cuisines.update(restaurant.cuisines)
    return CatalogStats(
        total_restaurants=len(restaurants),
        unique_cities=len(cities),
        unique_cuisines=len(cuisines),
    )


def load_quality_report(report_path: str) -> IngestionReport:
    path = Path(report_path)
    if not path.exists():
        raise CatalogFileError(f"Ingestion report not found at: {path}")
    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    return IngestionReport.model_validate(raw)
