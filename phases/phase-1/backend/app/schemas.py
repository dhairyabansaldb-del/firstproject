from typing import Optional

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    restaurant_id: str = Field(..., description="Stable generated ID for normalized row.")
    name: str
    location: str
    city: str
    cuisines: list[str]
    average_cost_for_two: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    votes: Optional[int] = Field(default=None, ge=0)
    source_dataset: str = "ManikaSaini/zomato-restaurant-recommendation"


class CatalogStats(BaseModel):
    total_restaurants: int
    unique_cities: int
    unique_cuisines: int


class CatalogQueryParams(BaseModel):
    city: Optional[str] = None
    cuisine: Optional[str] = None
    min_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    max_cost_for_two: Optional[float] = Field(default=None, ge=0.0)
    limit: int = Field(default=20, ge=1, le=100)
