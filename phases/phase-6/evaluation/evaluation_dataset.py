"""Offline evaluation dataset for recommendation quality assessment."""

import json
import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EvaluationScenario:
    """Single evaluation scenario with preferences and expected outcomes."""
    scenario_id: str
    name: str
    description: str
    preferences: Dict[str, Any]
    expected_constraints: Dict[str, Any]
    quality_criteria: Dict[str, Any]
    difficulty: str  # easy, medium, hard


@dataclass
class EvaluationResult:
    """Result of running a scenario through the recommendation system."""
    scenario_id: str
    recommendations: List[Dict[str, Any]]
    processing_time: float
    used_fallback: bool
    candidate_count: int
    quality_scores: Dict[str, float]
    errors: List[str]


class EvaluationDataset:
    """Comprehensive evaluation dataset for testing recommendation quality."""
    
    def __init__(self):
        self.scenarios = []
        self._create_scenarios()
    
    def _create_scenarios(self):
        """Create evaluation scenarios covering various use cases."""
        
        # Basic scenarios
        self.scenarios.extend([
            EvaluationScenario(
                scenario_id="basic_north_indian_bellandur",
                name="Basic North Indian in Bellandur",
                description="Simple request for North Indian cuisine in Bellandur area",
                preferences={
                    "location": "Bellandur",
                    "budget": "medium",
                    "cuisine": "North Indian",
                    "min_rating": 4.0,
                    "additional_preferences": [],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.0,
                    "budget_range": (800, 1500)
                },
                quality_criteria={
                    "relevance_weight": 0.4,
                    "diversity_weight": 0.3,
                    "explanation_weight": 0.3
                },
                difficulty="easy"
            ),
            
            EvaluationScenario(
                scenario_id="budget_friendly_chinese",
                name="Budget-Friendly Chinese",
                description="Low budget Chinese cuisine request",
                preferences={
                    "location": "HSR",
                    "budget": "low",
                    "cuisine": "Chinese",
                    "min_rating": 3.5,
                    "additional_preferences": ["quick-service"],
                    "limit": 3
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 3.5,
                    "max_cost": 800
                },
                quality_criteria={
                    "relevance_weight": 0.5,
                    "price_sensitivity_weight": 0.3,
                    "explanation_weight": 0.2
                },
                difficulty="easy"
            ),
            
            EvaluationScenario(
                scenario_id="high_end_italian",
                name="High-End Italian Dining",
                description="Premium Italian restaurant request",
                preferences={
                    "location": "Koramangala",
                    "budget": "high",
                    "cuisine": "Italian",
                    "min_rating": 4.5,
                    "additional_preferences": ["romantic"],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.5,
                    "min_cost": 1500
                },
                quality_criteria={
                    "relevance_weight": 0.3,
                    "premium_quality_weight": 0.4,
                    "explanation_weight": 0.3
                },
                difficulty="medium"
            )
        ])
        
        # Edge cases and challenging scenarios
        self.scenarios.extend([
            EvaluationScenario(
                scenario_id="very_high_rating_requirement",
                name="Very High Rating Requirement",
                description="Request for extremely high-rated restaurants",
                preferences={
                    "location": "Indiranagar",
                    "budget": "medium",
                    "cuisine": "Continental",
                    "min_rating": 4.9,
                    "additional_preferences": [],
                    "limit": 3
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.9
                },
                quality_criteria={
                    "relevance_weight": 0.6,
                    "fallback_handling_weight": 0.4
                },
                difficulty="hard"
            ),
            
            EvaluationScenario(
                scenario_id="specific_location_no_results",
                name="Specific Location with No Results",
                description="Request for location that might have limited options",
                preferences={
                    "location": "Electronic City",  # Might have limited data
                    "budget": "medium",
                    "cuisine": "Mexican",
                    "min_rating": 4.0,
                    "additional_preferences": ["family-friendly"],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.0
                },
                quality_criteria={
                    "fallback_handling_weight": 0.5,
                    "explanation_weight": 0.3,
                    "diversity_weight": 0.2
                },
                difficulty="hard"
            ),
            
            EvaluationScenario(
                scenario_id="multiple_cuisines_preference",
                name="Multiple Additional Preferences",
                description="Request with multiple additional preferences",
                preferences={
                    "location": "Marathahalli",
                    "budget": "medium",
                    "cuisine": "North Indian",
                    "min_rating": 4.0,
                    "additional_preferences": ["family-friendly", "outdoor-seating", "quick-service"],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.0
                },
                quality_criteria={
                    "relevance_weight": 0.4,
                    "preference_matching_weight": 0.3,
                    "explanation_weight": 0.3
                },
                difficulty="medium"
            ),
            
            EvaluationScenario(
                scenario_id="edge_case_min_budget",
                name="Minimum Budget Edge Case",
                description="Request with very low budget constraint",
                preferences={
                    "location": "Bellandur",
                    "budget": "low",
                    "cuisine": "South Indian",
                    "min_rating": 4.2,
                    "additional_preferences": [],
                    "limit": 3
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.2,
                    "max_cost": 800
                },
                quality_criteria={
                    "price_sensitivity_weight": 0.5,
                    "relevance_weight": 0.3,
                    "fallback_handling_weight": 0.2
                },
                difficulty="medium"
            )
        ])
        
        # Real-world scenarios
        self.scenarios.extend([
            EvaluationScenario(
                scenario_id="weekend_family_dinner",
                name="Weekend Family Dinner",
                description="Typical weekend family dining request",
                preferences={
                    "location": "Sarjapur Road",
                    "budget": "medium",
                    "cuisine": "North Indian",
                    "min_rating": 4.0,
                    "additional_preferences": ["family-friendly"],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.0
                },
                quality_criteria={
                    "relevance_weight": 0.4,
                    "family_suitability_weight": 0.3,
                    "explanation_weight": 0.3
                },
                difficulty="easy"
            ),
            
            EvaluationScenario(
                scenario_id="business_lunch_quick",
                name="Business Lunch - Quick Service",
                description="Quick business lunch requirement",
                preferences={
                    "location": "Koramangala",
                    "budget": "medium",
                    "cuisine": "Continental",
                    "min_rating": 4.0,
                    "additional_preferences": ["quick-service"],
                    "limit": 3
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.0
                },
                quality_criteria={
                    "relevance_weight": 0.4,
                    "speed_weight": 0.3,
                    "explanation_weight": 0.3
                },
                difficulty="medium"
            ),
            
            EvaluationScenario(
                scenario_id="date_night_romantic",
                name="Date Night - Romantic Setting",
                description="Romantic dinner for two",
                preferences={
                    "location": "Indiranagar",
                    "budget": "high",
                    "cuisine": "Italian",
                    "min_rating": 4.3,
                    "additional_preferences": ["romantic"],
                    "limit": 5
                },
                expected_constraints={
                    "location_match": True,
                    "cuisine_match": True,
                    "min_rating": 4.3,
                    "min_cost": 1500
                },
                quality_criteria={
                    "relevance_weight": 0.3,
                    "romance_suitability_weight": 0.4,
                    "explanation_weight": 0.3
                },
                difficulty="medium"
            )
        ])
    
    def get_scenarios_by_difficulty(self, difficulty: str) -> List[EvaluationScenario]:
        """Get scenarios filtered by difficulty level."""
        return [s for s in self.scenarios if s.difficulty == difficulty]
    
    def get_random_scenarios(self, count: int = 10) -> List[EvaluationScenario]:
        """Get random selection of scenarios."""
        return random.sample(self.scenarios, min(count, len(self.scenarios)))
    
    def get_all_scenarios(self) -> List[EvaluationScenario]:
        """Get all evaluation scenarios."""
        return self.scenarios.copy()
    
    def save_dataset(self, filepath: str):
        """Save dataset to file."""
        dataset_data = {
            "scenarios": [asdict(scenario) for scenario in self.scenarios],
            "metadata": {
                "total_scenarios": len(self.scenarios),
                "difficulty_distribution": {
                    difficulty: len([s for s in self.scenarios if s.difficulty == difficulty])
                    for difficulty in ["easy", "medium", "hard"]
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(dataset_data, f, indent=2)
    
    def load_dataset(self, filepath: str):
        """Load dataset from file."""
        with open(filepath, 'r') as f:
            dataset_data = json.load(f)
        
        self.scenarios = [
            EvaluationScenario(**scenario_data) 
            for scenario_data in dataset_data["scenarios"]
        ]


class QualityMetrics:
    """Calculate quality metrics for recommendation evaluation."""
    
    @staticmethod
    def calculate_relevance_score(recommendations: List[Dict[str, Any]], 
                                scenario: EvaluationScenario) -> float:
        """Calculate relevance score based on preference matching."""
        if not recommendations:
            return 0.0
        
        total_score = 0.0
        for rec in recommendations:
            score = 0.0
            
            # Check location matching
            if scenario.expected_constraints.get("location_match"):
                score += 0.25
            
            # Check cuisine matching
            if scenario.expected_constraints.get("cuisine_match"):
                score += 0.25
            
            # Check rating requirement
            min_rating = scenario.expected_constraints.get("min_rating", 0)
            if rec.get("rating", 0) >= min_rating:
                score += 0.25
            
            # Check budget constraints
            max_cost = scenario.expected_constraints.get("max_cost")
            min_cost = scenario.expected_constraints.get("min_cost")
            budget_range = scenario.expected_constraints.get("budget_range")
            
            cost = rec.get("average_cost_for_two", 0)
            if max_cost and cost <= max_cost:
                score += 0.25
            elif min_cost and cost >= min_cost:
                score += 0.25
            elif budget_range and budget_range[0] <= cost <= budget_range[1]:
                score += 0.25
            
            total_score += score
        
        return total_score / len(recommendations)
    
    @staticmethod
    def calculate_diversity_score(recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity score based on variety in recommendations."""
        if len(recommendations) <= 1:
            return 1.0
        
        # Check cuisine diversity
        cuisines = set()
        cost_ranges = set()
        rating_ranges = set()
        
        for rec in recommendations:
            # Cuisine diversity
            rec_cuisines = rec.get("cuisines", [])
            if rec_cuisines:
                cuisines.update(rec_cuisines)
            
            # Cost diversity
            cost = rec.get("average_cost_for_two", 0)
            if cost <= 800:
                cost_ranges.add("low")
            elif cost <= 1500:
                cost_ranges.add("medium")
            else:
                cost_ranges.add("high")
            
            # Rating diversity
            rating = rec.get("rating", 0)
            if rating < 4.0:
                rating_ranges.add("low")
            elif rating < 4.5:
                rating_ranges.add("medium")
            else:
                rating_ranges.add("high")
        
        # Calculate diversity score
        cuisine_diversity = min(len(cuisines) / len(recommendations), 1.0)
        cost_diversity = min(len(cost_ranges) / 3.0, 1.0)
        rating_diversity = min(len(rating_ranges) / 3.0, 1.0)
        
        return (cuisine_diversity + cost_diversity + rating_diversity) / 3.0
    
    @staticmethod
    def calculate_explanation_quality(recommendations: List[Dict[str, Any]]) -> float:
        """Calculate quality of explanations."""
        if not recommendations:
            return 0.0
        
        total_score = 0.0
        
        for rec in recommendations:
            explanation = rec.get("explanation", "")
            score = 0.0
            
            # Length check (not too short, not too long)
            if 10 <= len(explanation) <= 200:
                score += 0.3
            
            # Contains relevant keywords
            relevant_keywords = ["rating", "price", "budget", "cuisine", "location", "cost"]
            keyword_count = sum(1 for keyword in relevant_keywords if keyword.lower() in explanation.lower())
            score += min(keyword_count / len(relevant_keywords), 0.4)
            
            # Contains specific details
            if any(char.isdigit() for char in explanation):
                score += 0.3  # Contains numbers (ratings, costs)
            
            total_score += score
        
        return total_score / len(recommendations)
    
    @staticmethod
    def calculate_overall_quality(recommendations: List[Dict[str, Any]], 
                                 scenario: EvaluationScenario) -> Dict[str, float]:
        """Calculate overall quality scores."""
        relevance = QualityMetrics.calculate_relevance_score(recommendations, scenario)
        diversity = QualityMetrics.calculate_diversity_score(recommendations)
        explanation = QualityMetrics.calculate_explanation_quality(recommendations)
        
        # Apply scenario-specific weights
        weights = scenario.quality_criteria
        
        overall_score = (
            relevance * weights.get("relevance_weight", 0.33) +
            diversity * weights.get("diversity_weight", 0.33) +
            explanation * weights.get("explanation_weight", 0.34)
        )
        
        return {
            "relevance": relevance,
            "diversity": diversity,
            "explanation_quality": explanation,
            "overall_score": overall_score
        }


# Create and save the evaluation dataset
def create_evaluation_dataset():
    """Create and save the evaluation dataset."""
    dataset = EvaluationDataset()
    
    # Save to file
    output_path = "phases/phase-6/evaluation/evaluation_dataset.json"
    dataset.save_dataset(output_path)
    
    print(f"Evaluation dataset created with {len(dataset.scenarios)} scenarios")
    print(f"Saved to: {output_path}")
    
    # Print summary
    difficulty_dist = {
        difficulty: len(dataset.get_scenarios_by_difficulty(difficulty))
        for difficulty in ["easy", "medium", "hard"]
    }
    
    print(f"Difficulty distribution: {difficulty_dist}")
    
    return dataset


if __name__ == "__main__":
    create_evaluation_dataset()
