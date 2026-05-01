from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import (
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    RecommendationsRequest,
    RecommendationsResponse,
)
from .services import RecommendationService, Phase4ServiceError, Phase4NotFoundError

app = FastAPI(
    title=settings.app_name,
    version="5.0.0-phase5",
    description="Architecture Phase 5: User Experience and Result Presentation API.",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recommendation_service = RecommendationService()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint that also checks Phase 4 service."""
    phase4_healthy, phase4_status = await recommendation_service.check_phase4_health()
    
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        phase="phase-5",
        environment=settings.app_env,
        phase4_service_status=phase4_status if phase4_healthy else phase4_status,
    )


@app.post("/recommendations", response_model=RecommendationsResponse)
async def recommendations(request: RecommendationsRequest) -> RecommendationsResponse:
    """
    Get restaurant recommendations by proxying to Phase 4 service.
    
    This endpoint:
    - Validates the request
    - Forwards to Phase 4 recommendation service
    - Returns the response with enhanced error handling
    """
    try:
        recommendations = await recommendation_service.get_recommendations(request)
        return recommendations
        
    except Phase4NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Phase4ServiceError as e:
        # If Phase 4 service is down, return a helpful error
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Recommendation service unavailable",
                "message": str(e),
                "suggestion": "Please ensure the Phase 4 service is running on port 8401",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
            }
        )


@app.post("/feedback", response_model=FeedbackResponse)
async def feedback(feedback_request: FeedbackRequest) -> FeedbackResponse:
    """
    Store user feedback for recommendations.
    
    This endpoint:
    - Validates feedback data
    - Stores feedback with timestamp
    - Returns success/failure status
    """
    try:
        response = await recommendation_service.store_feedback(feedback_request)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to store feedback",
                "message": str(e),
            }
        )


@app.get("/feedback/stats")
async def feedback_stats():
    """
    Get feedback statistics.
    
    Returns aggregated feedback data for analysis.
    """
    try:
        stats = await recommendation_service.get_feedback_stats()
        return {
            "service": settings.app_name,
            "feedback_statistics": stats,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get feedback stats",
                "message": str(e),
            }
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "phase": "phase-5",
        "version": "5.0.0",
        "description": "User Experience and Result Presentation API",
        "endpoints": {
            "health": "/health",
            "recommendations": "/recommendations (POST)",
            "feedback": "/feedback (POST)",
            "feedback_stats": "/feedback/stats (GET)",
        },
        "phase4_service": settings.phase4_service_url,
    }
