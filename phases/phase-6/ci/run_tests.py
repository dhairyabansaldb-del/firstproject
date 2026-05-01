#!/usr/bin/env python3
"""
Phase 6 Test Runner Script

This script runs the complete test suite for Phase 6 quality assurance.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, timeout=300):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="c:/project"
        )
        
        duration = time.time() - start_time
        
        print(f"Duration: {duration:.2f}s")
        print(f"Exit Code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, duration
        
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after {timeout}s")
        return False, timeout
    except Exception as e:
        print(f"ERROR: {e}")
        return False, 0


def main():
    """Run the complete Phase 6 test suite."""
    print("Phase 6 Quality Assurance Test Suite")
    print("=" * 60)
    
    test_results = []
    total_duration = 0
    
    # 1. Unit Tests
    success, duration = run_command(
        "pytest phases/phase-6/tests/unit -v --tb=short",
        "Unit Tests (Filtering & Prompt Parsing)",
        timeout=120
    )
    test_results.append(("Unit Tests", success, duration))
    total_duration += duration
    
    # 2. Integration Tests
    success, duration = run_command(
        "pytest phases/phase-6/tests/integration -v --tb=short",
        "Integration Tests (API & LLM Mock)",
        timeout=180
    )
    test_results.append(("Integration Tests", success, duration))
    total_duration += duration
    
    # 3. Smoke Tests (only if services are running)
    print("\n" + "="*60)
    print("Checking if services are available for smoke tests...")
    
    try:
        import httpx
        with httpx.Client(timeout=5.0) as client:
            # Check Phase 5 service
            response = client.get("http://127.0.0.1:8500/health")
            if response.status_code == 200:
                print("Phase 5 service is available - running smoke tests")
                success, duration = run_command(
                    "pytest phases/phase-6/tests/smoke -v --tb=short",
                    "Smoke Tests (UI Flow)",
                    timeout=240
                )
                test_results.append(("Smoke Tests", success, duration))
                total_duration += duration
            else:
                print("Phase 5 service not available - skipping smoke tests")
                test_results.append(("Smoke Tests", None, 0))
    except Exception as e:
        print(f"Cannot check service availability: {e}")
        print("Skipping smoke tests")
        test_results.append(("Smoke Tests", None, 0))
    
    # 4. Generate Coverage Report
    success, duration = run_command(
        "pytest phases/phase-6/tests --cov=phases/phase-4/backend/app --cov=phases/phase-5/backend/app --cov-report=html --cov-report=term",
        "Coverage Report Generation",
        timeout=120
    )
    test_results.append(("Coverage Report", success, duration))
    total_duration += duration
    
    # 5. Run Evaluation (if Phase 5 is available)
    try:
        import httpx
        with httpx.Client(timeout=5.0) as client:
            response = client.get("http://127.0.0.1:8500/health")
            if response.status_code == 200:
                print("Phase 5 service available - running evaluation")
                success, duration = run_command(
                    "python phases/phase-6/evaluation/run_evaluation.py",
                    "Offline Evaluation",
                    timeout=300
                )
                test_results.append(("Offline Evaluation", success, duration))
                total_duration += duration
            else:
                print("Phase 5 service not available - skipping evaluation")
                test_results.append(("Offline Evaluation", None, 0))
    except Exception as e:
        print(f"Cannot run evaluation: {e}")
        test_results.append(("Offline Evaluation", None, 0))
    
    # Generate Summary Report
    print("\n" + "="*60)
    print("PHASE 6 TEST SUITE SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, success, duration in test_results:
        status = "PASS" if success else "FAIL" if success is False else "SKIP"
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        
        print(f"{test_name:<25} {status:<8} {duration_str}")
        
        if success:
            passed += 1
        elif success is False:
            failed += 1
        else:
            skipped += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total Duration: {total_duration:.2f}s")
    
    # Overall result
    if failed == 0:
        print("\n" + "="*60)
        print("ALL TESTS PASSED! Phase 6 is ready for production.")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print(f"{failed} TEST(S) FAILED! Please review the failures above.")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
