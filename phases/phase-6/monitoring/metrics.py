"""Metrics collection and monitoring for the restaurant recommendation system."""

import time
import threading
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetric:
    """Request-specific metric."""
    request_id: str
    method: str
    endpoint: str
    start_time: float
    end_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    duration: Optional[float] = None


class MetricsCollector:
    """Collects and aggregates system metrics."""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.lock = threading.RLock()
        
        # Time series data
        self.request_times = deque(maxlen=max_points)
        self.error_rates = deque(maxlen=max_points)
        self.response_sizes = deque(maxlen=max_points)
        
        # Counters
        self.request_counters = defaultdict(int)
        self.error_counters = defaultdict(int)
        self.status_code_counters = defaultdict(int)
        
        # Gauges
        self.active_requests = 0
        self.catalog_size = 0
        self.llm_calls = 0
        
        # Request tracking
        self.active_requests_map = {}
        self.completed_requests = deque(maxlen=max_points)
        
        # Performance metrics
        self.performance_thresholds = {
            "response_time": 2.0,  # seconds
            "error_rate": 5.0,     # percentage
            "memory_usage": 80.0   # percentage
        }
    
    def start_request(self, request_id: str, method: str, endpoint: str) -> None:
        """Start tracking a request."""
        with self.lock:
            self.active_requests += 1
            self.request_counters[f"{method}_{endpoint}"] += 1
            
            self.active_requests_map[request_id] = RequestMetric(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                start_time=time.time()
            )
    
    def end_request(self, request_id: str, status_code: int, 
                   response_size: int = 0, error: str = None) -> None:
        """End tracking a request."""
        with self.lock:
            if request_id not in self.active_requests_map:
                return
            
            request = self.active_requests_map.pop(request_id)
            request.end_time = time.time()
            request.status_code = status_code
            request.error = error
            request.duration = request.end_time - request.start_time
            
            # Update counters
            self.active_requests -= 1
            self.status_code_counters[status_code] += 1
            
            if status_code >= 400:
                self.error_counters[f"{request.method}_{request.endpoint}"] += 1
            
            # Store metrics
            self.request_times.append(MetricPoint(
                timestamp=request.end_time,
                value=request.duration,
                tags={"method": request.method, "endpoint": request.endpoint}
            ))
            
            self.response_sizes.append(MetricPoint(
                timestamp=request.end_time,
                value=response_size,
                tags={"method": request.method, "endpoint": request.endpoint}
            ))
            
            self.completed_requests.append(request)
    
    def record_llm_call(self, model: str, prompt_tokens: int, 
                        response_tokens: int, duration: float, 
                        success: bool) -> None:
        """Record LLM call metrics."""
        with self.lock:
            self.llm_calls += 1
            
            # Store LLM-specific metrics
            self.request_times.append(MetricPoint(
                timestamp=time.time(),
                value=duration,
                tags={"type": "llm_call", "model": model, "success": str(success)}
            ))
    
    def record_catalog_operation(self, operation: str, item_count: int, 
                               duration: float) -> None:
        """Record catalog operation metrics."""
        with self.lock:
            if operation == "load":
                self.catalog_size = item_count
            
            self.request_times.append(MetricPoint(
                timestamp=time.time(),
                value=duration,
                tags={"type": "catalog", "operation": operation}
            ))
    
    def record_feedback(self, feedback_type: str) -> None:
        """Record feedback metrics."""
        with self.lock:
            self.request_counters[f"feedback_{feedback_type}"] += 1
    
    def get_summary_metrics(self, time_window: int = 300) -> Dict[str, Any]:
        """Get summary metrics for the last time_window seconds."""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window
            
            # Filter recent metrics
            recent_requests = [
                r for r in self.completed_requests 
                if r.end_time and r.end_time > cutoff_time
            ]
            
            recent_response_times = [
                m for m in self.request_times 
                if m.timestamp > cutoff_time
            ]
            
            if not recent_requests:
                return self._empty_metrics()
            
            # Calculate basic metrics
            total_requests = len(recent_requests)
            successful_requests = len([r for r in recent_requests if 200 <= r.status_code < 400])
            error_requests = total_requests - successful_requests
            
            # Response time metrics
            response_times = [r.duration for r in recent_requests if r.duration]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            p95_response_time = self._percentile(response_times, 95) if response_times else 0
            p99_response_time = self._percentile(response_times, 99) if response_times else 0
            
            # Error rate
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Requests per minute
            requests_per_minute = total_requests / (time_window / 60) if time_window > 0 else 0
            
            # Status code distribution
            status_distribution = defaultdict(int)
            for request in recent_requests:
                status_distribution[request.status_code] += 1
            
            # Top endpoints by request count
            endpoint_counts = defaultdict(int)
            for request in recent_requests:
                endpoint_counts[f"{request.method} {request.endpoint}"] += 1
            top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "timestamp": current_time,
                "time_window_seconds": time_window,
                "request_metrics": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "error_requests": error_requests,
                    "requests_per_minute": round(requests_per_minute, 2),
                    "active_requests": self.active_requests
                },
                "performance_metrics": {
                    "avg_response_time": round(avg_response_time, 3),
                    "p95_response_time": round(p95_response_time, 3),
                    "p99_response_time": round(p99_response_time, 3),
                    "error_rate": round(error_rate, 2)
                },
                "status_distribution": dict(status_distribution),
                "top_endpoints": top_endpoints,
                "system_metrics": {
                    "catalog_size": self.catalog_size,
                    "total_llm_calls": self.llm_calls
                },
                "alerts": self._check_alerts(avg_response_time, error_rate)
            }
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            "timestamp": time.time(),
            "time_window_seconds": 300,
            "request_metrics": {
                "total_requests": 0,
                "successful_requests": 0,
                "error_requests": 0,
                "requests_per_minute": 0,
                "active_requests": self.active_requests
            },
            "performance_metrics": {
                "avg_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "error_rate": 0
            },
            "status_distribution": {},
            "top_endpoints": [],
            "system_metrics": {
                "catalog_size": self.catalog_size,
                "total_llm_calls": self.llm_calls
            },
            "alerts": []
        }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _check_alerts(self, avg_response_time: float, error_rate: float) -> List[Dict[str, Any]]:
        """Check for performance alerts."""
        alerts = []
        
        if avg_response_time > self.performance_thresholds["response_time"]:
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": f"Average response time ({avg_response_time:.3f}s) exceeds threshold ({self.performance_thresholds['response_time']}s)",
                "timestamp": time.time()
            })
        
        if error_rate > self.performance_thresholds["error_rate"]:
            alerts.append({
                "type": "error_rate",
                "severity": "critical",
                "message": f"Error rate ({error_rate:.2f}%) exceeds threshold ({self.performance_thresholds['error_rate']}%)",
                "timestamp": time.time()
            })
        
        return alerts
    
    def get_time_series_data(self, metric: str, time_window: int = 3600, 
                           interval: int = 60) -> List[Dict[str, Any]]:
        """Get time series data for a specific metric."""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window
            
            if metric == "response_time":
                data_points = [
                    m for m in self.request_times 
                    if m.timestamp > cutoff_time
                ]
            else:
                data_points = []
            
            # Aggregate by interval
            intervals = defaultdict(list)
            for point in data_points:
                interval_time = int(point.timestamp // interval) * interval
                intervals[interval_time].append(point.value)
            
            # Create time series
            time_series = []
            for interval_start in range(int(cutoff_time), int(current_time), interval):
                if interval_start in intervals:
                    values = intervals[interval_start]
                    time_series.append({
                        "timestamp": interval_start,
                        "value": sum(values) / len(values),
                        "count": len(values)
                    })
                else:
                    time_series.append({
                        "timestamp": interval_start,
                        "value": 0,
                        "count": 0
                    })
            
            return time_series
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        summary = self.get_summary_metrics()
        
        if format == "json":
            return json.dumps(summary, indent=2, default=str)
        else:
            return str(summary)


# Global metrics collector
metrics = MetricsCollector()


class PerformanceTracker:
    """Context manager for tracking performance of operations."""
    
    def __init__(self, operation: str, tags: Dict[str, str] = None):
        self.operation = operation
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        # Record the metric
        metrics.request_times.append(MetricPoint(
            timestamp=time.time(),
            value=duration,
            tags={"operation": self.operation, **self.tags}
        ))
        
        # Check for performance warnings
        if duration > metrics.performance_thresholds["response_time"]:
            from .logging import log_performance_warning
            log_performance_warning(self.operation, duration, 
                                   metrics.performance_thresholds["response_time"])


def track_performance(operation: str, tags: Dict[str, str] = None):
    """Decorator for tracking function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTracker(operation, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class HealthChecker:
    """Health checking for system components."""
    
    def __init__(self):
        self.checks = {}
    
    def add_check(self, name: str, check_func, timeout: float = 5.0):
        """Add a health check."""
        self.checks[name] = {
            "func": check_func,
            "timeout": timeout,
            "last_check": None,
            "status": "unknown"
        }
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check."""
        if name not in self.checks:
            return {"status": "error", "message": f"Check '{name}' not found"}
        
        check = self.checks[name]
        start_time = time.time()
        
        try:
            result = check["func"]()
            duration = time.time() - start_time
            
            check["last_check"] = time.time()
            check["status"] = "healthy" if result else "unhealthy"
            
            return {
                "status": check["status"],
                "duration": round(duration, 3),
                "timestamp": check["last_check"]
            }
            
        except Exception as e:
            duration = time.time() - start_time
            check["last_check"] = time.time()
            check["status"] = "unhealthy"
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "duration": round(duration, 3),
                "timestamp": check["last_check"]
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_healthy = True
        
        for name in self.checks:
            results[name] = self.run_check(name)
            if results[name]["status"] != "healthy":
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "checks": results,
            "timestamp": time.time()
        }


# Global health checker
health_checker = HealthChecker()
