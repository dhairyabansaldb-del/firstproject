import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ..schemas import CatalogStats, Restaurant


class CatalogNotFoundError(FileNotFoundError):
    pass


@lru_cache(maxsize=1)
def load_catalog(catalog_path: str) -> list[Restaurant]:
    path = Path(catalog_path)
    if not path.exists():
        raise CatalogNotFoundError(f"Catalog file not found at: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_rows = json.load(file)

    return [Restaurant.model_validate(row) for row in raw_rows]


def filter_restaurants(
    restaurants: list[Restaurant],
    city: Optional[str] = None,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_cost_for_two: Optional[float] = None,
    limit: int = 20,
) -> list[Restaurant]:
    filtered = restaurants

    if city:
        city_cmp = city.strip().lower()
        filtered = [r for r in filtered if r.city.lower() == city_cmp]

    if cuisine:
        cuisine_cmp = cuisine.strip().lower()
        filtered = [
            r
            for r in filtered
            if any(cuisine_cmp == c.lower() for c in r.cuisines)
        ]

    if min_rating is not None:
        filtered = [
            r for r in filtered if r.rating is not None and r.rating >= min_rating
        ]

    if max_cost_for_two is not None:
        filtered = [
            r
            for r in filtered
            if r.average_cost_for_two is not None
            and r.average_cost_for_two <= max_cost_for_two
        ]

    return filtered[:limit]


def compute_stats(restaurants: list[Restaurant]) -> CatalogStats:
    cities = {r.city for r in restaurants}
    cuisines: set[str] = set()
    for restaurant in restaurants:
        cuisines.update(restaurant.cuisines)

    return CatalogStats(
        total_restaurants=len(restaurants),
        unique_cities=len(cities),
        unique_cuisines=len(cuisines),
    )
