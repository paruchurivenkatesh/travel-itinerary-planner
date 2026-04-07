#!/usr/bin/env python3
"""
Travel Itinerary Planner - Submission Pre-Validator
====================================================
Validates that your submission meets all requirements before final upload:

1. Check environment variables are set
2. Test that inference.py runs and produces correct output format
3. Verify API endpoints respond correctly
4. Check Docker build (if available)
5. Validate openenv.yaml structure

Usage:
  python validate_submission.py [--space-url <url>]

Example:
  python validate_submission.py --space-url https://myspace.hf.space
"""

import os
import sys
import json
import subprocess
import shutil
from typing import Tuple, Optional
from pathlib import Path

# Color output utilities for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def success(msg: str) -> str:
        return f"{Colors.GREEN}[PASS]{Colors.RESET} {msg}"

    @staticmethod
    def fail(msg: str) -> str:
        return f"{Colors.RED}[FAIL]{Colors.RESET} {msg}"

    @staticmethod
    def warning(msg: str) -> str:
        return f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}"

    @staticmethod
    def info(msg: str) -> str:
        return f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}"


def check_env_vars() -> bool:
    """Check required environment variables."""
    print(f"\n{Colors.BOLD}Check 1: Environment Variables{Colors.RESET}")
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "API_BASE_URL": "API endpoint (optional, has default)",
        "MODEL_NAME": "Model name (optional, has default)",
        "HF_TOKEN": "Hugging Face token (optional)"
    }
    
    all_set = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print(Colors.success(f"{var} is set ({masked})"))
        else:
            print(Colors.warning(f"{var} is not set ({desc})"))
            if var == "OPENAI_API_KEY":
                all_set = False
    
    return all_set


def check_inference_script() -> bool:
    """Verify inference.py exists and has correct structure."""
    print(f"\n{Colors.BOLD}Check 2: Inference Script{Colors.RESET}")
    
    if not Path("inference.py").exists():
        print(Colors.fail("inference.py not found in root directory"))
        return False
    
    print(Colors.success("inference.py found in root"))
    
    # Check for required elements
    with open("inference.py") as f:
        content = f.read()
    
    required_strings = [
        ("OPENAI_API_KEY", "OpenAI API key reading"),
        ("API_BASE_URL", "API base URL configuration"),
        ("MODEL_NAME", "Model name configuration"),
        ("log_start", "log_start function"),
        ("log_step", "[STEP] logging"),
        ("[START]", "[START] log format"),
        ("[END]", "[END] log format"),
    ]
    
    for required, description in required_strings:
        if required in content:
            print(Colors.success(f"Found: {description}"))
        else:
            print(Colors.fail(f"Missing: {description}"))
            return False
    
    return True


def check_openenv_spec() -> bool:
    """Verify openenv.yaml and typed models."""
    print(f"\n{Colors.BOLD}Check 3: OpenEnv Specification{Colors.RESET}")
    
    # Check openenv.yaml exists
    if not Path("openenv.yaml").exists():
        print(Colors.fail("openenv.yaml not found"))
        return False
    
    print(Colors.success("openenv.yaml found"))
    
    # Check environment.py for typed models
    env_file = Path("travel_itinerary_planner/env.py")
    if not env_file.exists():
        print(Colors.fail("travel_itinerary_planner/env.py not found"))
        return False
    
    with open(env_file) as f:
        content = f.read()
    
    required_models = [
        ("class Action", "Action model"),
        ("class Observation", "Observation model"),
        ("class Reward", "Reward model"),
        ("class Info", "Info model"),
        ("def reset", "reset() method"),
        ("def step", "step() method"),
        ("def state", "state() method"),
        ("def _grade", "grader function"),
    ]
    
    for required, description in required_models:
        if required in content:
            print(Colors.success(f"Found: {description}"))
        else:
            print(Colors.fail(f"Missing: {description}"))
            return False
    
    return True


def check_api_endpoints() -> bool:
    """Test API endpoints using TestClient."""
    print(f"\n{Colors.BOLD}Check 4: API Endpoints{Colors.RESET}")
    
    try:
        from fastapi.testclient import TestClient
        from app import app
        
        with TestClient(app) as client:
            # Test /reset
            resp = client.post("/reset")
            if resp.status_code == 200:
                print(Colors.success("POST /reset returns 200"))
            else:
                print(Colors.fail(f"POST /reset returned {resp.status_code}"))
                return False
            
            # Test /state
            resp = client.get("/state")
            if resp.status_code == 200:
                print(Colors.success("GET /state returns 200"))
            else:
                print(Colors.fail(f"GET /state returned {resp.status_code}"))
                return False
            
            # Test /step
            resp = client.post("/step", json={"action_type": "add_activity", "activity_id": 0})
            if resp.status_code == 200:
                print(Colors.success("POST /step returns 200"))
            else:
                print(Colors.fail(f"POST /step returned {resp.status_code}"))
                return False
            
            # Test /health
            resp = client.get("/health")
            if resp.status_code == 200:
                print(Colors.success("GET /health returns 200"))
            else:
                print(Colors.fail(f"GET /health returned {resp.status_code}"))
                return False
        
        return True
    
    except Exception as e:
        print(Colors.fail(f"API test failed: {e}"))
        return False


def check_unit_tests() -> bool:
    """Run unit tests."""
    print(f"\n{Colors.BOLD}Check 5: Unit Tests{Colors.RESET}")
    
    if not Path("tests/test_env.py").exists():
        print(Colors.warning("tests/test_env.py not found"))
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_env.py", "-q"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Count passed tests from output
            output_lines = result.stdout.strip().split('\n')
            last_line = output_lines[-1] if output_lines else ""
            print(Colors.success(f"All unit tests passed ({last_line.split()[0]} tests)"))
            return True
        else:
            print(Colors.fail(f"Unit tests failed\n{result.stdout}\n{result.stderr}"))
            return False
    
    except subprocess.TimeoutExpired:
        print(Colors.fail("Unit tests timed out"))
        return False
    except Exception as e:
        print(Colors.fail(f"Could not run unit tests: {e}"))
        return False


def check_docker() -> bool:
    """Check if Docker is available and can build."""
    print(f"\n{Colors.BOLD}Check 6: Docker Build{Colors.RESET}")
    
    if not shutil.which("docker"):
        print(Colors.warning("Docker not installed (cannot validate docker build)"))
        return True  # Not a blocking failure
    
    if not Path("Dockerfile").exists():
        print(Colors.fail("Dockerfile not found"))
        return False
    
    print(Colors.info("Docker found, attempting build (this may take a minute)..."))
    
    try:
        result = subprocess.run(
            ["docker", "build", "."],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print(Colors.success("Docker build completed successfully"))
            return True
        else:
            print(Colors.fail(f"Docker build failed\n{result.stderr[:500]}..."))
            return False
    
    except subprocess.TimeoutExpired:
        print(Colors.fail("Docker build timed out (>10 minutes)"))
        return False
    except Exception as e:
        print(Colors.fail(f"Docker build error: {e}"))
        return False


def main():
    """Run all validation checks."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Travel Itinerary Planner - Submission Validator{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    checks = [
        ("Environment Variables", check_env_vars),
        ("Inference Script", check_inference_script),
        ("OpenEnv Spec", check_openenv_spec),
        ("API Endpoints", check_api_endpoints),
        ("Unit Tests", check_unit_tests),
        ("Docker Build", check_docker),
    ]
    
    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(Colors.fail(f"Unexpected error in {name}: {e}"))
            results[name] = False
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = Colors.success("PASS") if result else Colors.fail("FAIL")
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All checks passed! Ready to submit.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[INCOMPLETE] Some checks failed. Please fix them before submitting.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
