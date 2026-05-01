from typing import Optional

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    restaurant_id: str = Field(..., description="Stable ID generated after normalization.")
    name: str
    location: str
    city: str
    cuisines: list[str]
    average_cost_for_two: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    votes: Optional[int] = Field(default=None, ge=0)
    source_dataset: str


class CatalogStats(BaseModel):
    total_restaurants: int
    unique_cities: int
    unique_cuisines: int


class IngestionReport(BaseModel):
    source_dataset: str
    total_input_rows: int
    total_kept_rows: int
    dropped_missing_required: int
    dropped_duplicates: int
    dropped_invalid_rating: int
