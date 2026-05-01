#!/usr/bin/env python3
"""
Phase 5 Backend Runner Script

This script provides a convenient way to run the Phase 5 backend service
with proper configuration and error handling.
"""

import uvicorn
from app.config import settings


def main():
    """Run the Phase 5 backend service."""
    print(f"Starting {settings.app_name}...")
    print(f"Environment: {settings.app_env}")
    print(f"Phase 4 Service: {settings.phase4_service_url}")
    print(f"Frontend Origin: {settings.frontend_origin}")
    print(f"Server: http://{settings.app_host}:{settings.app_port}")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.app_host,
            port=settings.app_port,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting server: {e}")


if __name__ == "__main__":
    main()
