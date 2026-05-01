from typing import Any, Optional

from ..schemas import BudgetTier, CandidateRestaurant, RecommendationsRequest

# Cost bands for "average_cost_for_two"
BUDGET_RANGES = {
    BudgetTier.low: (0.0, 800.0),
    BudgetTier.medium: (800.0, 1500.0),
    BudgetTier.high: (1500.0, 1000000.0),
}


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _matches_location(row: dict[str, Any], location: str) -> bool:
    needle = _normalize_text(location)
    return needle in _normalize_text(str(row.get("city", ""))) or needle in _normalize_text(
        str(row.get("location", ""))
    )


def _matches_cuisine(row: dict[str, Any], cuisine: Optional[str]) -> bool:
    if not cuisine:
        return True
    needle = _normalize_text(cuisine)
    return any(needle in _normalize_text(str(item)) for item in row.get("cuisines", []))


def _matches_budget(row: dict[str, Any], budget: BudgetTier) -> bool:
    min_cost, max_cost = BUDGET_RANGES[budget]
    cost = row.get("average_cost_for_two")
    if cost is None:
        return False
    try:
        return min_cost < float(cost) <= max_cost
    except (TypeError, ValueError):
        return False


def _matches_rating(row: dict[str, Any], min_rating: Optional[float]) -> bool:
    if min_rating is None:
        return True
    rating = row.get("rating")
    if rating is None:
        return False
    try:
        return float(rating) >= min_rating
    except (TypeError, ValueError):
        return False


def build_candidates(
    catalog: list[dict[str, Any]], request: RecommendationsRequest
) -> list[CandidateRestaurant]:
    filtered = []
    for row in catalog:
        if not _matches_location(row, request.location):
            continue
        if not _matches_cuisine(row, request.cuisine):
            continue
        if not _matches_rating(row, request.min_rating):
            continue
        if not _matches_budget(row, request.budget):
            continue
        filtered.append(row)

    ordered = sorted(
        filtered,
        key=lambda row: (
            -(float(row.get("rating") or 0.0)),
            -(int(row.get("votes") or 0)),
            float(row.get("average_cost_for_two") or 999999),
        ),
    )[:50]

    return [
        CandidateRestaurant(
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
            rating=float(row["rating"]) if row.get("rating") is not None else None,
            votes=int(row["votes"]) if row.get("votes") is not None else None,
        )
        for row in ordered
    ]
