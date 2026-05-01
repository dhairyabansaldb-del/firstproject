"""Run comprehensive evaluation of the recommendation system."""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import httpx
from pathlib import Path

from evaluation_dataset import EvaluationDataset, EvaluationResult, QualityMetrics


class RecommendationEvaluator:
    """Evaluate recommendation system performance."""
    
    def __init__(self, phase5_url: str = "http://127.0.0.1:8500"):
        self.phase5_url = phase5_url
        self.results = []
    
    async def run_scenario(self, scenario, http_client: httpx.AsyncClient) -> EvaluationResult:
        """Run a single evaluation scenario."""
        start_time = time.time()
        errors = []
        
        try:
            # Make recommendation request
            response = await http_client.post(
                f"{self.phase5_url}/recommendations",
                json=scenario.preferences,
                timeout=30.0
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                candidate_lookup = data.get("candidate_lookup", [])
                
                # Match recommendations with full restaurant data
                full_recommendations = []
                for rec in recommendations:
                    restaurant = next(
                        (r for r in candidate_lookup if r["restaurant_id"] == rec["restaurant_id"]),
                        None
                    )
                    if restaurant:
                        full_recommendations.append({
                            **restaurant,
                            "rank": rec["rank"],
                            "explanation": rec["explanation"]
                        })
                
                # Calculate quality scores
                quality_scores = QualityMetrics.calculate_overall_quality(
                    full_recommendations, scenario
                )
                
                return EvaluationResult(
                    scenario_id=scenario.scenario_id,
                    recommendations=full_recommendations,
                    processing_time=processing_time,
                    used_fallback=data.get("used_fallback", False),
                    candidate_count=data.get("total_candidates_considered", 0),
                    quality_scores=quality_scores,
                    errors=errors
                )
                
            else:
                errors.append(f"HTTP {response.status_code}: {response.text}")
                return EvaluationResult(
                    scenario_id=scenario.scenario_id,
                    recommendations=[],
                    processing_time=processing_time,
                    used_fallback=True,
                    candidate_count=0,
                    quality_scores={"relevance": 0, "diversity": 0, "explanation_quality": 0, "overall_score": 0},
                    errors=errors
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            errors.append(str(e))
            
            return EvaluationResult(
                scenario_id=scenario.scenario_id,
                recommendations=[],
                processing_time=processing_time,
                used_fallback=True,
                candidate_count=0,
                quality_scores={"relevance": 0, "diversity": 0, "explanation_quality": 0, "overall_score": 0},
                errors=errors
            )
    
    async def run_evaluation(self, scenarios: List) -> List[EvaluationResult]:
        """Run evaluation on multiple scenarios."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [self.run_scenario(scenario, client) for scenario in scenarios]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and convert to results
            evaluation_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    evaluation_results.append(EvaluationResult(
                        scenario_id=scenarios[i].scenario_id,
                        recommendations=[],
                        processing_time=0,
                        used_fallback=True,
                        candidate_count=0,
                        quality_scores={"relevance": 0, "diversity": 0, "explanation_quality": 0, "overall_score": 0},
                        errors=[str(result)]
                    ))
                else:
                    evaluation_results.append(result)
            
            self.results = evaluation_results
            return evaluation_results
    
    def generate_report(self, results: List[EvaluationResult], scenarios: List) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        if not results:
            return {"error": "No results to report"}
        
        # Basic statistics
        total_scenarios = len(results)
        successful_scenarios = len([r for r in results if not r.errors])
        scenarios_with_fallback = len([r for r in results if r.used_fallback])
        
        # Performance metrics
        processing_times = [r.processing_time for r in results if r.processing_time > 0]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Quality metrics
        overall_scores = [r.quality_scores["overall_score"] for r in results]
        relevance_scores = [r.quality_scores["relevance"] for r in results]
        diversity_scores = [r.quality_scores["diversity"] for r in results]
        explanation_scores = [r.quality_scores["explanation_quality"] for r in results]
        
        # Calculate averages
        avg_overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        avg_relevance_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        avg_diversity_score = sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0
        avg_explanation_score = sum(explanation_scores) / len(explanation_scores) if explanation_scores else 0
        
        # Performance by difficulty
        difficulty_stats = {}
        for difficulty in ["easy", "medium", "hard"]:
            diff_scenarios = [s for s in scenarios if s.difficulty == difficulty]
            diff_results = [r for r in results if any(s.scenario_id == r.scenario_id for s in diff_scenarios)]
            
            if diff_results:
                diff_scores = [r.quality_scores["overall_score"] for r in diff_results]
                diff_times = [r.processing_time for r in diff_results if r.processing_time > 0]
                
                difficulty_stats[difficulty] = {
                    "count": len(diff_results),
                    "avg_score": sum(diff_scores) / len(diff_scores),
                    "avg_time": sum(diff_times) / len(diff_times) if diff_times else 0,
                    "success_rate": len([r for r in diff_results if not r.errors]) / len(diff_results) * 100
                }
        
        # Error analysis
        error_analysis = {}
        for result in results:
            if result.errors:
                for error in result.errors:
                    error_type = error.split(':')[0] if ':' in error else 'unknown'
                    error_analysis[error_type] = error_analysis.get(error_type, 0) + 1
        
        # Recommendations analysis
        total_recommendations = sum(len(r.recommendations) for r in results)
        avg_recommendations_per_scenario = total_recommendations / total_scenarios if total_scenarios > 0 else 0
        
        # Top performing scenarios
        scenario_performances = []
        for result in results:
            scenario = next(s for s in scenarios if s.scenario_id == result.scenario_id)
            scenario_performances.append({
                "scenario_id": result.scenario_id,
                "scenario_name": scenario.name,
                "difficulty": scenario.difficulty,
                "score": result.quality_scores["overall_score"],
                "processing_time": result.processing_time,
                "used_fallback": result.used_fallback,
                "recommendation_count": len(result.recommendations)
            })
        
        # Sort by score
        scenario_performances.sort(key=lambda x: x["score"], reverse=True)
        top_performers = scenario_performances[:5]
        worst_performers = scenario_performances[-5:]
        
        # Generate recommendations
        recommendations = []
        
        if avg_overall_score < 0.7:
            recommendations.append("Overall recommendation quality is below target - consider improving LLM prompts or fallback logic")
        
        if scenarios_with_fallback / total_scenarios > 0.3:
            recommendations.append("High fallback usage detected - investigate data coverage or LLM reliability")
        
        if avg_processing_time > 3.0:
            recommendations.append("Processing time is above target - consider optimization")
        
        if avg_explanation_score < 0.6:
            recommendations.append("Explanation quality needs improvement - enhance prompt engineering")
        
        return {
            "metadata": {
                "evaluation_timestamp": datetime.now().isoformat(),
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
                "scenarios_with_fallback": scenarios_with_fallback,
                "fallback_rate": (scenarios_with_fallback / total_scenarios * 100) if total_scenarios > 0 else 0
            },
            "performance_metrics": {
                "avg_processing_time": round(avg_processing_time, 3),
                "total_recommendations_generated": total_recommendations,
                "avg_recommendations_per_scenario": round(avg_recommendations_per_scenario, 1)
            },
            "quality_metrics": {
                "avg_overall_score": round(avg_overall_score, 3),
                "avg_relevance_score": round(avg_relevance_score, 3),
                "avg_diversity_score": round(avg_diversity_score, 3),
                "avg_explanation_score": round(avg_explanation_score, 3)
            },
            "difficulty_breakdown": difficulty_stats,
            "error_analysis": error_analysis,
            "top_performing_scenarios": top_performers,
            "worst_performing_scenarios": worst_performers,
            "recommendations": recommendations,
            "detailed_results": [
                {
                    "scenario_id": result.scenario_id,
                    "scenario_name": next(s.name for s in scenarios if s.scenario_id == result.scenario_id),
                    "difficulty": next(s.difficulty for s in scenarios if s.scenario_id == result.scenario_id),
                    "processing_time": result.processing_time,
                    "used_fallback": result.used_fallback,
                    "candidate_count": result.candidate_count,
                    "recommendation_count": len(result.recommendations),
                    "quality_scores": result.quality_scores,
                    "errors": result.errors
                }
                for result in results
            ]
        }
    
    def save_report(self, report: Dict[str, Any], filepath: str):
        """Save evaluation report to file."""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Evaluation report saved to: {filepath}")


async def run_full_evaluation():
    """Run the complete evaluation suite."""
    print("Starting Phase 6 Evaluation Suite...")
    print("=" * 50)
    
    # Load evaluation dataset
    print("Loading evaluation dataset...")
    dataset = EvaluationDataset()
    scenarios = dataset.get_all_scenarios()
    
    print(f"Loaded {len(scenarios)} evaluation scenarios")
    print(f"Difficulty distribution:")
    for difficulty in ["easy", "medium", "hard"]:
        count = len(dataset.get_scenarios_by_difficulty(difficulty))
        print(f"  {difficulty}: {count} scenarios")
    
    print("\nRunning evaluation scenarios...")
    
    # Run evaluation
    evaluator = RecommendationEvaluator()
    results = await evaluator.run_evaluation(scenarios)
    
    print(f"Completed {len(results)} scenario evaluations")
    
    # Generate report
    print("\nGenerating evaluation report...")
    report = evaluator.generate_report(results, scenarios)
    
    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total Scenarios: {report['metadata']['total_scenarios']}")
    print(f"Success Rate: {report['metadata']['success_rate']:.1f}%")
    print(f"Fallback Rate: {report['metadata']['fallback_rate']:.1f}%")
    print(f"Avg Processing Time: {report['performance_metrics']['avg_processing_time']:.3f}s")
    print(f"Avg Overall Score: {report['quality_metrics']['avg_overall_score']:.3f}")
    print(f"Avg Relevance Score: {report['quality_metrics']['avg_relevance_score']:.3f}")
    print(f"Avg Diversity Score: {report['quality_metrics']['avg_diversity_score']:.3f}")
    print(f"Avg Explanation Score: {report['quality_metrics']['avg_explanation_score']:.3f}")
    
    # Print difficulty breakdown
    print("\nPerformance by Difficulty:")
    for difficulty, stats in report['difficulty_breakdown'].items():
        print(f"  {difficulty.capitalize()}:")
        print(f"    Score: {stats['avg_score']:.3f}")
        print(f"    Time: {stats['avg_time']:.3f}s")
        print(f"    Success Rate: {stats['success_rate']:.1f}%")
    
    # Print top performers
    print("\nTop Performing Scenarios:")
    for i, scenario in enumerate(report['top_performing_scenarios'][:3], 1):
        print(f"  {i}. {scenario['scenario_name']} ({scenario['difficulty']}) - Score: {scenario['score']:.3f}")
    
    # Print recommendations
    if report['recommendations']:
        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Save detailed report
    output_dir = Path("phases/phase-6/evaluation")
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / "evaluation_report.json"
    evaluator.save_report(report, str(report_file))
    
    # Save results for further analysis
    results_file = output_dir / "evaluation_results.json"
    results_data = {
        "metadata": report["metadata"],
        "results": [
            {
                "scenario_id": result.scenario_id,
                "processing_time": result.processing_time,
                "used_fallback": result.used_fallback,
                "candidate_count": result.candidate_count,
                "quality_scores": result.quality_scores,
                "recommendations": result.recommendations,
                "errors": result.errors
            }
            for result in results
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return report


if __name__ == "__main__":
    # Run the evaluation
    asyncio.run(run_full_evaluation())
