import json
from typing import Optional

from groq import Groq

from ..schemas import CandidateRestaurant, RankedRecommendation, RecommendationsRequest


class LLMRankingError(Exception):
    pass


def _strip_json_block(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


def _build_prompt(
    request: RecommendationsRequest, candidates: list[CandidateRestaurant], limit: int
) -> str:
    candidate_payload = [
        {
            "restaurant_id": c.restaurant_id,
            "name": c.name,
            "location": c.location,
            "city": c.city,
            "cuisines": c.cuisines,
            "average_cost_for_two": c.average_cost_for_two,
            "rating": c.rating,
            "votes": c.votes,
        }
        for c in candidates
    ]
    request_payload = request.model_dump()
    
    # Define budget ranges for clarity
    budget_ranges = {
        "low": "0-800 (strictly less than 800)",
        "medium": "800-1500 (greater than 800, up to 1500)",
        "high": "1500+ (strictly greater than 1500)"
    }
    
    budget_range = budget_ranges.get(request.budget, "any")
    
    return (
        "You are a restaurant ranking assistant.\n"
        "Rank only from the provided candidates.\n"
        f"IMPORTANT: Budget constraint is '{request.budget}' which means cost must be {budget_range}.\n"
        "STRICTLY enforce budget constraints - do not recommend restaurants outside the specified budget range.\n"
        "If the user has specified 'additional_preferences' in their JSON, your explanation MUST explicitly state why the restaurant is a perfect fit for those specific categories.\n"
        "Return only valid JSON in this shape:\n"
        "{\n"
        '  "recommendations": [\n'
        '    {"restaurant_id":"...", "rank":1, "explanation":"..." }\n'
        "  ]\n"
        "}\n"
        f"Return exactly top {limit} recommendations.\n"
        "No markdown, no extra keys, no text outside JSON.\n\n"
        f"User preferences JSON:\n{json.dumps(request_payload, ensure_ascii=True)}\n\n"
        f"Candidate restaurants JSON:\n{json.dumps(candidate_payload, ensure_ascii=True)}\n"
    )


# Global client instance to avoid connection issues
_groq_client = None

def get_groq_client(api_key: str) -> Groq:
    """Get or create Groq client instance"""
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def rank_with_groq(
    *,
    api_key: str,
    model: str,
    request: RecommendationsRequest,
    candidates: list[CandidateRestaurant],
    limit: int,
) -> list[RankedRecommendation]:
    if not api_key:
        raise LLMRankingError("Missing GROQ_API_KEY.")

    client = get_groq_client(api_key)
    prompt = _build_prompt(request=request, candidates=candidates, limit=limit)

    import time
    
    # Retry logic for reliability
    max_retries = 2
    retry_delay = 1.0
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                max_tokens=1000,  # Limit response length
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict JSON generator for ranking tasks.",
                    },
                    {"role": "user", "content": prompt},
                ],
                timeout=10.0  # Add explicit timeout
            )
            break  # Success, exit retry loop
        except Exception as e:
            if attempt == max_retries:
                raise LLMRankingError(f"Failed after {max_retries} retries: {str(e)}")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    content: Optional[str] = None
    if response.choices:
        content = response.choices[0].message.content
    if not content:
        raise LLMRankingError("Empty response from Groq model.")

    cleaned = _strip_json_block(content)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMRankingError(f"Invalid JSON from model: {exc}") from exc

    raw_recs = payload.get("recommendations")
    if not isinstance(raw_recs, list):
        raise LLMRankingError("JSON missing 'recommendations' list.")

    parsed = [RankedRecommendation.model_validate(item) for item in raw_recs]

    # Remove duplicates by restaurant_id
    seen_ids = set()
    unique_recs = []
    for rec in parsed:
        if rec.restaurant_id not in seen_ids:
            seen_ids.add(rec.restaurant_id)
            unique_recs.append(rec)
    
    # Keep exact top N and normalize rank order
    unique_recs = unique_recs[:limit]
    for idx, rec in enumerate(unique_recs, start=1):
        rec.rank = idx
    return unique_recs
