from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BudgetTier(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecommendationsRequest(BaseModel):
    location: str = Field(..., min_length=2)
    budget: BudgetTier
    cuisine: Optional[str] = Field(default=None, min_length=2)
    min_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    additional_preferences: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=20)


class CandidateRestaurant(BaseModel):
    restaurant_id: str
    name: str
    location: str
    city: str
    cuisines: list[str]
    average_cost_for_two: Optional[float] = None
    rating: Optional[float] = None
    votes: Optional[int] = None


class RankedRecommendation(BaseModel):
    restaurant_id: str
    rank: int = Field(..., ge=1)
    explanation: str = Field(..., min_length=10)


class RecommendationsResponse(BaseModel):
    request: RecommendationsRequest
    total_candidates_considered: int
    used_fallback: bool
    fallback_reason: Optional[str] = None
    recommendations: list[RankedRecommendation]
    candidate_lookup: list[CandidateRestaurant]
