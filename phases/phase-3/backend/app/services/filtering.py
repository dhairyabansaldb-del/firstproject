from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..schemas import AppliedRelaxation, BudgetTier, RecommendationPreviewRequest

# Cost bands for "average_cost_for_two"
BUDGET_RANGES = {
    BudgetTier.low: (0.0, 800.0),
    BudgetTier.medium: (800.0, 1500.0),
    BudgetTier.high: (1500.0, 1000000.0),
}


@dataclass
class FilteringResult:
    matches: list[dict[str, Any]]
    relaxations: list[AppliedRelaxation]


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _matches_location(row: dict[str, Any], location: str) -> bool:
    needle = _normalize_text(location)
    city = _normalize_text(str(row.get("city", "")))
    locality = _normalize_text(str(row.get("location", "")))
    return needle in city or needle in locality


def _matches_cuisine(row: dict[str, Any], cuisine: Optional[str]) -> bool:
    if not cuisine:
        return True
    needle = _normalize_text(cuisine)
    cuisines = [str(item).strip().lower() for item in row.get("cuisines", [])]
    return any(needle in item for item in cuisines)


def _matches_budget(row: dict[str, Any], budget: BudgetTier) -> bool:
    min_cost, max_cost = BUDGET_RANGES[budget]
    cost = row.get("average_cost_for_two")
    if cost is None:
        return False
    try:
        cost_float = float(cost)
        return min_cost < cost_float <= max_cost
    except (ValueError, TypeError):
        return False


def _matches_rating(row: dict[str, Any], min_rating: Optional[float]) -> bool:
    if min_rating is None:
        return True
    rating = row.get("rating")
    if rating is None:
        return False
    try:
        return float(rating) >= min_rating
    except (ValueError, TypeError):
        return False


def _apply_filters(
    catalog: list[dict[str, Any]],
    request: RecommendationPreviewRequest,
    *,
    rating_override: Optional[float] = None,
    cuisine_override: Optional[str] = None,
    budget_override: Optional[BudgetTier] = None,
) -> list[dict[str, Any]]:
    min_rating = request.min_rating if rating_override is None else rating_override
    cuisine = request.cuisine if cuisine_override is None else cuisine_override
    budget = request.budget if budget_override is None else budget_override

    results = []
    for row in catalog:
        if not _matches_location(row, request.location):
            continue
        if not _matches_cuisine(row, cuisine):
            continue
        if not _matches_rating(row, min_rating):
            continue
        if not _matches_budget(row, budget):
            continue
        results.append(row)
    return results


def run_filtering_with_fallbacks(
    catalog: list[dict[str, Any]],
    request: RecommendationPreviewRequest,
) -> FilteringResult:
    # Step 1: strict match
    strict = _apply_filters(catalog, request)
    if strict:
        return FilteringResult(matches=strict, relaxations=[])

    relaxations: list[AppliedRelaxation] = []

    # Step 2: relax min rating by 0.5, then 1.0
    if request.min_rating is not None:
        relaxed_05 = max(0.0, request.min_rating - 0.5)
        matches = _apply_filters(catalog, request, rating_override=relaxed_05)
        relaxations.append(
            AppliedRelaxation(
                step="rating_relaxation",
                detail=f"Lowered min_rating from {request.min_rating} to {relaxed_05}",
            )
        )
        if matches:
            return FilteringResult(matches=matches, relaxations=relaxations)

        relaxed_10 = max(0.0, request.min_rating - 1.0)
        matches = _apply_filters(catalog, request, rating_override=relaxed_10)
        relaxations.append(
            AppliedRelaxation(
                step="rating_relaxation",
                detail=f"Lowered min_rating further to {relaxed_10}",
            )
        )
        if matches:
            return FilteringResult(matches=matches, relaxations=relaxations)

    # Step 3: remove cuisine constraint
    if request.cuisine:
        matches = _apply_filters(catalog, request, cuisine_override=None)
        relaxations.append(
            AppliedRelaxation(
                step="cuisine_relaxation",
                detail="Removed strict cuisine constraint.",
            )
        )
        if matches:
            return FilteringResult(matches=matches, relaxations=relaxations)

    # Step 4: widen budget one tier upward
    next_budget = None
    if request.budget == BudgetTier.low:
        next_budget = BudgetTier.medium
    elif request.budget == BudgetTier.medium:
        next_budget = BudgetTier.high

    if next_budget is not None:
        matches = _apply_filters(catalog, request, budget_override=next_budget)
        relaxations.append(
            AppliedRelaxation(
                step="budget_relaxation",
                detail=f"Widened budget from {request.budget.value} to {next_budget.value}.",
            )
        )
        if matches:
            return FilteringResult(matches=matches, relaxations=relaxations)

    return FilteringResult(matches=[], relaxations=relaxations)
