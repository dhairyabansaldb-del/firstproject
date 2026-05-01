import sys
from pathlib import Path
from typing import Dict, List

import pytest
import httpx

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add phase backends to path
phase2_path = project_root / "phases" / "phase-2" / "backend"
phase3_path = project_root / "phases" / "phase-3" / "backend"
phase4_path = project_root / "phases" / "phase-4" / "backend"
phase5_path = project_root / "phases" / "phase-5" / "backend"

sys.path.insert(0, str(phase2_path))
sys.path.insert(0, str(phase3_path))
sys.path.insert(0, str(phase4_path))
sys.path.insert(0, str(phase5_path))


@pytest.fixture
def sample_restaurants():
    """Sample restaurant data for testing."""
    return [
        {
            "restaurant_id": "test1",
            "name": "Test Restaurant 1",
            "location": "Bellandur",
            "city": "Bellandur",
            "cuisines": ["North Indian", "Chinese"],
            "average_cost_for_two": 1000.0,
            "rating": 4.5,
            "votes": 1000
        },
        {
            "restaurant_id": "test2",
            "name": "Test Restaurant 2",
            "location": "Marathahalli",
            "city": "Bellandur",
            "cuisines": ["South Indian", "Italian"],
            "average_cost_for_two": 800.0,
            "rating": 4.2,
            "votes": 500
        },
        {
            "restaurant_id": "test3",
            "name": "Test Restaurant 3",
            "location": "Sarjapur Road",
            "city": "Bellandur",
            "cuisines": ["North Indian", "Mughlai"],
            "average_cost_for_two": 1200.0,
            "rating": 4.8,
            "votes": 2000
        },
        {
            "restaurant_id": "test4",
            "name": "Test Restaurant 4",
            "location": "HSR",
            "city": "Bellandur",
            "cuisines": ["Chinese", "Continental"],
            "average_cost_for_two": 600.0,
            "rating": 3.9,
            "votes": 300
        }
    ]


@pytest.fixture
def sample_preferences():
    """Sample user preferences for testing."""
    return {
        "location": "Bellandur",
        "budget": "medium",
        "cuisine": "North Indian",
        "min_rating": 4.0,
        "additional_preferences": ["family-friendly"],
        "limit": 5
    }


@pytest.fixture
def catalog_file(tmp_path, sample_restaurants):
    """Create a temporary catalog file for testing."""
    import json
    
    catalog_path = tmp_path / "test_catalog.json"
    with open(catalog_path, 'w') as f:
        json.dump(sample_restaurants, f)
    
    return str(catalog_path)


@pytest.fixture
def http_client():
    """HTTP client for API testing."""
    return httpx.Client(timeout=30.0)


@pytest.fixture
def service_urls():
    """Base URLs for all services."""
    return {
        "phase2": "http://127.0.0.1:8200",
        "phase3": "http://127.0.0.1:8300",
        "phase4": "http://127.0.0.1:8401",
        "phase5": "http://127.0.0.1:8500",
        "frontend": "http://127.0.0.1:5500"
    }


# Helper functions for testing
def assert_valid_recommendation(recommendation):
    """Assert that a recommendation has valid structure."""
    assert "restaurant_id" in recommendation
    assert "rank" in recommendation
    assert "explanation" in recommendation
    assert isinstance(recommendation["rank"], int)
    assert recommendation["rank"] > 0
    assert len(recommendation["explanation"]) > 0


def assert_valid_restaurant(restaurant):
    """Assert that a restaurant has valid structure."""
    required_fields = ["restaurant_id", "name", "location", "city", "cuisines", "average_cost_for_two", "rating", "votes"]
    for field in required_fields:
        assert field in restaurant, f"Missing field: {field}"
    
    assert isinstance(restaurant["cuisines"], list)
    assert len(restaurant["cuisines"]) > 0
    assert 0 <= restaurant["rating"] <= 5
    assert restaurant["average_cost_for_two"] > 0
    assert restaurant["votes"] >= 0
