from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationsRequest(BaseModel):
    location: str = Field(..., description="Location for restaurant search")
    budget: str = Field(..., description="Budget category: low, medium, high")
    cuisine: str = Field(..., description="Preferred cuisine type")
    min_rating: float = Field(..., ge=3.0, le=5.0, description="Minimum rating")
    additional_preferences: List[str] = Field(default_factory=list, description="Additional preferences")
    limit: int = Field(default=5, ge=1, le=20, description="Number of recommendations to return")


class RankedRecommendation(BaseModel):
    restaurant_id: str
    rank: int
    explanation: str


class CandidateRestaurant(BaseModel):
    restaurant_id: str
    name: str
    location: str
    city: str
    cuisines: List[str]
    average_cost_for_two: float
    rating: float
    votes: int


class RecommendationsResponse(BaseModel):
    request: RecommendationsRequest
    total_candidates_considered: int
    used_fallback: bool
    fallback_reason: Optional[str] = None
    recommendations: List[RankedRecommendation]
    candidate_lookup: List[CandidateRestaurant]


class FeedbackRequest(BaseModel):
    restaurant_id: str
    feedback: str = Field(..., pattern="^(helpful|not-helpful)$", description="Feedback type")
    preferences: RecommendationsRequest
    timestamp: str


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    phase: str
    environment: str
    phase4_service_status: Optional[str] = None
