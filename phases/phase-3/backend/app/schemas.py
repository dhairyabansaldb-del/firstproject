from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BudgetTier(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecommendationPreviewRequest(BaseModel):
    location: str = Field(..., min_length=2, description="City or locality")
    budget: BudgetTier
    cuisine: Optional[str] = Field(default=None, min_length=2)
    min_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    additional_preferences: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=50)


class RestaurantCandidate(BaseModel):
    restaurant_id: str
    name: str
    location: str
    city: str
    cuisines: list[str]
    average_cost_for_two: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    votes: Optional[int] = None


class AppliedRelaxation(BaseModel):
    step: str
    detail: str


class RecommendationPreviewResponse(BaseModel):
    request: RecommendationPreviewRequest
    matched_count: int
    used_fallback: bool
    applied_relaxations: list[AppliedRelaxation]
    candidates: list[RestaurantCandidate]
