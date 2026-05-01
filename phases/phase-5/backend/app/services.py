import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException

from .config import settings
from .schemas import (
    FeedbackRequest,
    FeedbackResponse,
    RecommendationsRequest,
    RecommendationsResponse,
)


class Phase4ServiceError(Exception):
    """Exception raised when Phase 4 service is unavailable or returns errors."""
    pass

class Phase4NotFoundError(Exception):
    """Exception raised when Phase 4 service returns 404 Not Found."""
    pass


class FeedbackService:
    """Simple in-memory feedback storage for Phase 5 demonstration."""
    
    def __init__(self):
        self.feedback_store: List[Dict] = []
    
    def store_feedback(self, feedback_request: FeedbackRequest) -> FeedbackResponse:
        """Store user feedback and return response."""
        try:
            feedback_id = str(uuid.uuid4())
            feedback_entry = {
                "id": feedback_id,
                "restaurant_id": feedback_request.restaurant_id,
                "feedback": feedback_request.feedback,
                "preferences": feedback_request.preferences.model_dump(),
                "timestamp": feedback_request.timestamp,
                "stored_at": datetime.utcnow().isoformat(),
            }
            
            self.feedback_store.append(feedback_entry)
            
            return FeedbackResponse(
                success=True,
                message="Feedback recorded successfully",
                feedback_id=feedback_id
            )
        except Exception as e:
            return FeedbackResponse(
                success=False,
                message=f"Failed to store feedback: {str(e)}"
            )
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics."""
        total = len(self.feedback_store)
        helpful = sum(1 for f in self.feedback_store if f["feedback"] == "helpful")
        not_helpful = total - helpful
        
        return {
            "total_feedback": total,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful,
            "helpful_percentage": (helpful / total * 100) if total > 0 else 0
        }


class RecommendationService:
    """Service for handling recommendations by proxying to Phase 4."""
    
    def __init__(self):
        self.feedback_service = FeedbackService()
    
    async def get_recommendations(
        self, 
        request: RecommendationsRequest
    ) -> RecommendationsResponse:
        """Get recommendations from Phase 4 service."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.phase4_recommendations_url,
                    json=request.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return RecommendationsResponse.model_validate(data)
                elif response.status_code == 404:
                    raise Phase4NotFoundError("No restaurant found for the given criteria.")
                else:
                    error_text = response.text
                    raise Phase4ServiceError(
                        f"Phase 4 service returned {response.status_code}: {error_text}"
                    )
                    
        except Phase4NotFoundError:
            raise
        except httpx.TimeoutException:
            raise Phase4ServiceError("Phase 4 service timeout")
        except httpx.ConnectError:
            raise Phase4ServiceError("Cannot connect to Phase 4 service")
        except Exception as e:
            raise Phase4ServiceError(f"Unexpected error: {str(e)}")
    
    async def store_feedback(self, feedback_request: FeedbackRequest) -> FeedbackResponse:
        """Store user feedback."""
        return self.feedback_service.store_feedback(feedback_request)
    
    async def get_feedback_stats(self) -> Dict:
        """Get feedback statistics."""
        return self.feedback_service.get_feedback_stats()
    
    async def check_phase4_health(self) -> Tuple[bool, Optional[str]]:
        """Check if Phase 4 service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                health_url = f"{settings.phase4_service_url}/health"
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    return True, "healthy"
                else:
                    return False, f"unhealthy (status: {response.status_code})"
                    
        except httpx.TimeoutException:
            return False, "timeout"
        except httpx.ConnectError:
            return False, "connection_failed"
        except Exception as e:
            return False, f"error: {str(e)}"
