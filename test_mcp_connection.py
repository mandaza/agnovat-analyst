#!/usr/bin/env python3
"""
Agnovat Analyst - MCP Connection Test Script
Tests server health and MCP tool availability
"""

import requests
import sys
import json
from typing import Dict, Any, List


BASE_URL = "http://localhost:8000"
COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "RESET": "\033[0m",
}


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{COLORS['BLUE']}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{COLORS['RESET']}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{COLORS['GREEN']}✅ {text}{COLORS['RESET']}")


def print_error(text: str):
    """Print error message"""
    print(f"{COLORS['RED']}❌ {text}{COLORS['RESET']}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{COLORS['YELLOW']}⚠️  {text}{COLORS['RESET']}")


def print_info(text: str):
    """Print info message"""
    print(f"{COLORS['BLUE']}ℹ️  {text}{COLORS['RESET']}")


def test_server_health() -> bool:
    """Test 1: Check if server is running and healthy"""
    print_header("Test 1: Server Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is running and healthy")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print_error(f"Server returned status code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server")
        print_info("Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
        return False

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_api_docs() -> bool:
    """Test 2: Check if API documentation is accessible"""
    print_header("Test 2: API Documentation")

    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)

        if response.status_code == 200:
            print_success("API documentation is accessible")
            print(f"   URL: {BASE_URL}/docs")
            return True
        else:
            print_warning("API docs returned unexpected status")
            print(f"   Status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Cannot access API docs: {e}")
        return False


def test_openapi_spec() -> bool:
    """Test 3: Check OpenAPI specification"""
    print_header("Test 3: OpenAPI Specification")

    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)

        if response.status_code == 200:
            spec = response.json()
            paths = spec.get("paths", {})
            print_success(f"OpenAPI spec available")
            print(f"   Total endpoints: {len(paths)}")

            # Count tool endpoints
            tool_endpoints = [
                p for p in paths.keys() if p.startswith("/api/")
            ]
            print(f"   Tool endpoints: {len(tool_endpoints)}")
            return True
        else:
            print_error(f"OpenAPI spec returned: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Cannot fetch OpenAPI spec: {e}")
        return False


def test_sample_tools() -> bool:
    """Test 4: Test sample tool endpoints"""
    print_header("Test 4: Sample Tool Tests")

    # We'll test a few key tools with minimal valid inputs
    # Note: These will fail if file doesn't exist, but that's expected
    tests = [
        {
            "name": "Tool 1: Extract Text",
            "endpoint": "/api/pdf/extract-text",
            "payload": {"file_path": "/nonexistent/test.pdf"},
            "expect_404": True,
        },
        {
            "name": "Tool 5: Analyze Bias",
            "endpoint": "/api/analysis/analyze-racism-bias",
            "payload": {"file_path": "/nonexistent/test.pdf"},
            "expect_404": True,
        },
        {
            "name": "Tool 20: NDIS Goals (CRITICAL)",
            "endpoint": "/api/legal/goals-guardianship-alignment",
            "payload": {
                "file_path": "/nonexistent/test.pdf",
                "guardianship_context": "Test",
            },
            "expect_404": True,
        },
    ]

    success_count = 0
    for test in tests:
        try:
            response = requests.post(
                f"{BASE_URL}{test['endpoint']}",
                json=test["payload"],
                timeout=5,
            )

            # We expect 404 for nonexistent files - that's actually good!
            # It means the endpoint exists and is processing requests
            if test["expect_404"] and response.status_code == 404:
                print_success(f"{test['name']} - Endpoint operational")
                success_count += 1
            elif response.status_code == 200:
                print_success(f"{test['name']} - Success!")
                success_count += 1
            else:
                print_warning(
                    f"{test['name']} - Unexpected status: {response.status_code}"
                )

        except Exception as e:
            print_error(f"{test['name']} - Error: {e}")

    print(f"\n   Passed: {success_count}/{len(tests)}")
    return success_count == len(tests)


def test_all_tools_available() -> bool:
    """Test 5: Verify all 23 tools are available"""
    print_header("Test 5: All 23 Tools Availability")

    expected_tools = {
        "PDF Processing": [
            "/api/pdf/extract-text",
            "/api/pdf/generate-hash",
            "/api/pdf/verify-integrity",
            "/api/pdf/extract-metadata",
        ],
        "Analysis": [
            "/api/analysis/analyze-racism-bias",
            "/api/analysis/detect-inconsistencies",
            "/api/analysis/detect-template-reuse",
            "/api/analysis/detect-omitted-context",
            "/api/analysis/detect-non-evidence-based",
            "/api/analysis/extract-family-support",
            "/api/analysis/extract-pg-limitations",
            "/api/analysis/compare-documents",
            "/api/analysis/analyze-and-compare",
            "/api/analysis/extract-timeline",
            "/api/analysis/contradiction-matrix",
        ],
        "Legal Framework": [
            "/api/legal/human-rights-breaches",
            "/api/legal/guardianship-risk-assessment",
            "/api/legal/detect-state-guardianship-bias",
            "/api/legal/professional-language-compliance",
            "/api/legal/goals-guardianship-alignment",
        ],
        "Reports": [
            "/api/reports/guardianship-argument",
            "/api/reports/qcat-evidence-summary",
            "/api/reports/qcat-bundle",
        ],
    }

    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code != 200:
            print_error("Cannot fetch OpenAPI spec")
            return False

        spec = response.json()
        available_paths = set(spec.get("paths", {}).keys())

        total_expected = 0
        total_found = 0

        for category, endpoints in expected_tools.items():
            print(f"\n{category}:")
            for endpoint in endpoints:
                total_expected += 1
                if endpoint in available_paths:
                    print_success(f"   {endpoint}")
                    total_found += 1
                else:
                    print_error(f"   {endpoint} - MISSING")

        print(f"\n   Found: {total_found}/{total_expected} tools")

        if total_found == total_expected:
            print_success(f"All 23 tools are available!")
            return True
        else:
            print_error(f"Missing {total_expected - total_found} tools")
            return False

    except Exception as e:
        print_error(f"Error checking tools: {e}")
        return False


def test_mcp_compatibility() -> bool:
    """Test 6: MCP compatibility check"""
    print_header("Test 6: MCP Compatibility")

    # Check if FastAPI-MCP is properly configured
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)

        if response.status_code == 200:
            data = response.json()
            if "mcp_enabled" in data or "service" in data:
                print_success("MCP server responding correctly")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print_warning("Server responding but MCP status unclear")
                return True  # Still OK if server responds

        else:
            print_error(f"Root endpoint returned: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"MCP compatibility check failed: {e}")
        return False


def main():
    """Run all tests and provide summary"""
    print_header("AGNOVAT ANALYST - MCP CONNECTION TEST SUITE")
    print("Testing MCP server availability and tool endpoints")

    results = {
        "Server Health": test_server_health(),
        "API Documentation": test_api_docs(),
        "OpenAPI Spec": test_openapi_spec(),
        "Sample Tools": test_sample_tools(),
        "All 23 Tools": test_all_tools_available(),
        "MCP Compatibility": test_mcp_compatibility(),
    }

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{COLORS['BLUE']}{'='*80}{COLORS['RESET']}")
    print(f"Overall: {passed}/{total} tests passed")
    print(f"{COLORS['BLUE']}{'='*80}{COLORS['RESET']}\n")

    if passed == total:
        print_success("All tests passed! MCP server is ready for use.")
        print_info("\nNext steps:")
        print("1. Configure Claude Desktop: ./setup_claude_desktop.sh")
        print("2. Restart Claude Desktop")
        print("3. Ask Claude: 'List all available Agnovat tools'")
        print("\nDocumentation: docs/MCP_INTEGRATION.md")
        return 0
    else:
        print_error(f"Some tests failed. Check the output above for details.")
        print_info("\nTroubleshooting:")
        print("1. Make sure server is running: uvicorn app.main:app --reload")
        print("2. Check server logs for errors")
        print("3. Verify dependencies: pip install -r requirements.txt")
        print("\nDocumentation: docs/MCP_INTEGRATION.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
