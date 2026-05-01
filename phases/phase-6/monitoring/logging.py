"""Structured logging configuration for observability."""

import structlog
import logging
import time
import uuid
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Get structured logger
logger = structlog.get_logger()


class RequestMetrics:
    """Request metrics collector."""
    
    def __init__(self):
        self.requests = []
        self.current_request = None
    
    def start_request(self, method: str, endpoint: str, request_id: str = None) -> str:
        """Start tracking a request."""
        request_id = request_id or str(uuid.uuid4())
        self.current_request = {
            "request_id": request_id,
            "method": method,
            "endpoint": endpoint,
            "start_time": time.time(),
            "status": "pending"
        }
        return request_id
    
    def end_request(self, request_id: str, status_code: int, error: str = None):
        """End tracking a request."""
        if self.current_request and self.current_request["request_id"] == request_id:
            self.current_request["end_time"] = time.time()
            self.current_request["duration"] = (
                self.current_request["end_time"] - self.current_request["start_time"]
            )
            self.current_request["status_code"] = status_code
            self.current_request["error"] = error
            self.current_request["status"] = "completed"
            
            self.requests.append(self.current_request.copy())
            self.current_request = None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        if not self.requests:
            return {
                "total_requests": 0,
                "avg_latency": 0,
                "success_rate": 100.0,
                "error_rate": 0.0,
                "requests_per_minute": 0
            }
        
        total_requests = len(self.requests)
        successful_requests = len([r for r in self.requests if 200 <= r.get("status_code", 0) < 400])
        avg_latency = sum(r["duration"] for r in self.requests) / total_requests
        
        # Calculate requests per minute (last 5 minutes)
        current_time = time.time()
        recent_requests = [
            r for r in self.requests 
            if current_time - r["end_time"] <= 300
        ]
        requests_per_minute = len(recent_requests) / 5.0 if recent_requests else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "avg_latency": round(avg_latency, 3),
            "success_rate": round((successful_requests / total_requests) * 100, 2),
            "error_rate": round(((total_requests - successful_requests) / total_requests) * 100, 2),
            "requests_per_minute": round(requests_per_minute, 2)
        }


# Global metrics instance
metrics = RequestMetrics()


def log_request(method: str, endpoint: str, request_data: Dict[str, Any] = None):
    """Decorator to log HTTP requests."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = metrics.start_request(method, endpoint)
            
            logger.info(
                "Request started",
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                request_data=request_data
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                logger.info(
                    "Request completed successfully",
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint
                )
                
                metrics.end_request(request_id, 200)
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Log error
                logger.error(
                    "Request failed",
                    request_id=request_id,
                    method=method,
                    endpoint=endpoint,
                    error=error_msg,
                    exc_info=True
                )
                
                metrics.end_request(request_id, 500, error_msg)
                raise
        
        return wrapper
    return decorator


def log_api_call(service: str, operation: str, **kwargs):
    """Log API calls to external services."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "API call started",
        request_id=request_id,
        service=service,
        operation=operation,
        **kwargs
    )
    
    @contextmanager
    def context():
        try:
            yield request_id
            
            duration = time.time() - start_time
            logger.info(
                "API call completed successfully",
                request_id=request_id,
                service=service,
                operation=operation,
                duration=round(duration, 3)
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "API call failed",
                request_id=request_id,
                service=service,
                operation=operation,
                duration=round(duration, 3),
                error=str(e),
                exc_info=True
            )
            raise
    
    return context()


def log_recommendation_request(preferences: Dict[str, Any], candidates_count: int, 
                             used_fallback: bool, processing_time: float):
    """Log recommendation request details."""
    logger.info(
        "Recommendation request processed",
        location=preferences.get("location"),
        budget=preferences.get("budget"),
        cuisine=preferences.get("cuisine"),
        min_rating=preferences.get("min_rating"),
        candidates_considered=candidates_count,
        used_fallback=used_fallback,
        processing_time=round(processing_time, 3),
        additional_preferences=preferences.get("additional_preferences", [])
    )


def log_llm_interaction(prompt_length: int, response_length: int, 
                        processing_time: float, model: str, success: bool):
    """Log LLM interaction details."""
    logger.info(
        "LLM interaction",
        model=model,
        prompt_length=prompt_length,
        response_length=response_length,
        processing_time=round(processing_time, 3),
        success=success
    )


def log_feedback_submission(restaurant_id: str, feedback: str, 
                          preferences: Dict[str, Any]):
    """Log feedback submission."""
    logger.info(
        "Feedback submitted",
        restaurant_id=restaurant_id,
        feedback=feedback,
        location=preferences.get("location"),
        cuisine=preferences.get("cuisine")
    )


def log_system_event(event_type: str, **kwargs):
    """Log system events."""
    logger.info(
        f"System event: {event_type}",
        event_type=event_type,
        **kwargs
    )


def log_performance_warning(operation: str, duration: float, threshold: float):
    """Log performance warnings."""
    logger.warning(
        "Performance warning",
        operation=operation,
        duration=round(duration, 3),
        threshold=threshold,
        message=f"Operation took longer than expected threshold of {threshold}s"
    )


def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        format="%(message)s",
        stream=open("phases/phase-6/monitoring/logs/app.log", "a"),
        level=getattr(logging, level.upper())
    )


class RequestContext:
    """Request context for logging."""
    
    def __init__(self, request_id: str = None, user_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.start_time = time.time()
        self.context_data = {}
    
    def add_context(self, key: str, value: Any):
        """Add context data."""
        self.context_data[key] = value
    
    def get_context(self) -> Dict[str, Any]:
        """Get all context data."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "start_time": self.start_time,
            **self.context_data
        }


# Request context manager
@contextmanager
def request_context(request_id: str = None, user_id: str = None):
    """Context manager for request logging."""
    context = RequestContext(request_id, user_id)
    
    # Bind context to logger
    logger = structlog.get_logger().bind(**context.get_context())
    
    try:
        yield logger, context
    finally:
        duration = time.time() - context.start_time
        logger.info("Request context ended", duration=round(duration, 3))


# Error tracking
class ErrorTracker:
    """Track and analyze errors."""
    
    def __init__(self):
        self.errors = []
    
    def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """Record an error occurrence."""
        error_info = {
            "timestamp": time.time(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "stack_trace": traceback.format_exc() if traceback else None
        }
        self.errors.append(error_info)
        
        # Log the error
        logger.error(
            "Error recorded",
            error_type=error_info["error_type"],
            error_message=error_info["error_message"],
            context=error_info["context"]
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        if not self.errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "recent_errors": []
            }
        
        # Count error types
        error_types = {}
        for error in self.errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Get recent errors (last hour)
        current_time = time.time()
        recent_errors = [
            error for error in self.errors
            if current_time - error["timestamp"] <= 3600
        ]
        
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "recent_errors": len(recent_errors),
            "error_rate": len(recent_errors) / 60.0  # errors per minute
        }


# Global error tracker
error_tracker = ErrorTracker()


import traceback
