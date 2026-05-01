from typing import Optional, Any

from ..config import settings
from ..schemas import CandidateRestaurant, RankedRecommendation, RecommendationsRequest
from .fallback import deterministic_fallback
from .llm_groq import LLMRankingError, rank_with_groq


def _validate_ids(
    recommendations: list[RankedRecommendation], candidates: list[CandidateRestaurant]
) -> None:
    valid_ids = {c.restaurant_id for c in candidates}
    for rec in recommendations:
        if rec.restaurant_id not in valid_ids:
            raise LLMRankingError(
                f"Model returned unknown restaurant_id: {rec.restaurant_id}"
            )


def _deterministic_ranking(candidates: list[dict[str, Any]], limit: int) -> list[RankedRecommendation]:
    """Deterministic ranking based on rating and votes"""
    # Sort by rating (descending) then by votes (descending)
    sorted_candidates = sorted(
        candidates, 
        key=lambda x: (getattr(x, 'rating', None) or 0.0, getattr(x, 'votes', None) or 0), 
        reverse=True
    )
    
    recommendations = []
    for i, candidate in enumerate(sorted_candidates[:limit]):
        rating_val = getattr(candidate, 'rating', None) or 0.0
        votes_val = getattr(candidate, 'votes', None) or 0
        rec = RankedRecommendation(
            restaurant_id=getattr(candidate, 'restaurant_id', ''),
            rank=i + 1,
            explanation=f"Ranked {i+1} based on rating {rating_val} and {votes_val} votes"
        )
        recommendations.append(rec)
    
    return recommendations


_recommendation_cache = {}

def generate_ranked_recommendations(
    request: RecommendationsRequest, candidates: list[dict[str, Any]]
) -> tuple[list[RankedRecommendation], bool, Optional[str]]:
    import hashlib
    import json
    global _recommendation_cache
    
    cache_key_data = {
        "req": request.model_dump(),
        "candidates": [getattr(c, "restaurant_id", "") for c in candidates]
    }
    cache_key = hashlib.sha1(json.dumps(cache_key_data, sort_keys=True).encode("utf-8")).hexdigest()
    
    if cache_key in _recommendation_cache:
        return _recommendation_cache[cache_key]
        
    result = _generate_ranked_impl(request, candidates)
    _recommendation_cache[cache_key] = result
    return result

def _generate_ranked_impl(
    request: RecommendationsRequest, candidates: list[dict[str, Any]]
) -> tuple[list[RankedRecommendation], bool, Optional[str]]:
    """
    Generate ranked recommendations using deterministic ranking with LLM enhancement.
    
    This function prioritizes system reliability over AI ranking to ensure
    consistent performance for deployment.

    Returns:
        (recommendations, used_fallback, fallback_reason)
    """
    # Always start with deterministic ranking for reliability
    ranked = _deterministic_ranking(candidates, request.limit)
    
    # Try LLM enhancement in background if available
    try:
        if settings.groq_api_key:
            import threading
            import time
            
            llm_result = []
            llm_error = None
            
            def try_llm():
                nonlocal llm_result, llm_error
                try:
                    sorted_c = sorted(
                        candidates,
                        key=lambda x: (getattr(x, 'rating', None) or 0.0, getattr(x, 'votes', None) or 0),
                        reverse=True
                    )[:15]
                    llm_ranked = rank_with_groq(
                        api_key=settings.groq_api_key,
                        model=settings.groq_model,
                        request=request,
                        candidates=[CandidateRestaurant.model_validate(c) for c in sorted_c],
                        limit=request.limit,
                    )
                    llm_result = llm_ranked
                except Exception as e:
                    llm_error = str(e)
            
            # Try LLM with short timeout
            thread = threading.Thread(target=try_llm)
            thread.daemon = True
            thread.start()
            thread.join(timeout=5.0)  # 5 second timeout for LLM
            
            if thread.is_alive():
                # LLM took too long, use deterministic ranking
                return ranked, True, "LLM timeout - using deterministic ranking"
            elif llm_error:
                # LLM failed, use deterministic ranking
                return ranked, True, f"LLM error - using deterministic ranking: {llm_error}"
            elif llm_result:
                # LLM succeeded, use AI ranking
                return llm_result, False, None
            else:
                # LLM returned empty, use deterministic ranking
                return ranked, True, "LLM returned empty - using deterministic ranking"
        else:
            return ranked, True, "No API key - using deterministic ranking"
            
    except Exception as e:
        # Any error, fall back to deterministic
        return ranked, True, f"System error - using deterministic ranking: {str(e)}"
