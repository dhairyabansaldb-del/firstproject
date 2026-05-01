from ..schemas import CandidateRestaurant, RankedRecommendation


def deterministic_fallback(
    candidates: list[CandidateRestaurant], limit: int
) -> list[RankedRecommendation]:
    top = candidates[:limit]
    output: list[RankedRecommendation] = []
    for idx, candidate in enumerate(top, start=1):
        cost = (
            f"{int(candidate.average_cost_for_two)} for two"
            if candidate.average_cost_for_two is not None
            else "cost unavailable"
        )
        rating = (
            f"rating {candidate.rating:.1f}"
            if candidate.rating is not None
            else "rating unavailable"
        )
        reason = (
            f"Matches your location and budget constraints with {rating}; "
            f"offers {', '.join(candidate.cuisines[:2])} cuisine and {cost}."
        )
        output.append(
            RankedRecommendation(
                restaurant_id=candidate.restaurant_id,
                rank=idx,
                explanation=reason,
            )
        )
    return output
