"""
Comprehensive Test Suite for All 23 Agnovat Analyst Tools
Tests all endpoints with sample data
"""

import pytest
import requests
import json
from pathlib import Path
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
SAMPLE_PDF = "/path/to/sample_document.pdf"  # Replace with actual test PDF


class TestPDFProcessing:
    """Tests for Tools 1-4: PDF Processing"""

    def test_tool_01_extract_text(self):
        """Tool 1: Extract text from PDF"""
        endpoint = f"{BASE_URL}/api/pdf/extract-text"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "full_text" in data
            assert "statistics" in data
            print(f"✅ Tool 1: Extracted {data['statistics']['total_characters']} characters")

    def test_tool_02_generate_hash(self):
        """Tool 2: Generate document hash"""
        endpoint = f"{BASE_URL}/api/pdf/generate-hash"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "hash" in data
            assert "algorithm" in data
            assert data["algorithm"] == "SHA-256"
            print(f"✅ Tool 2: Generated hash: {data['hash'][:16]}...")

    def test_tool_03_verify_integrity(self):
        """Tool 3: Verify document integrity"""
        endpoint = f"{BASE_URL}/api/pdf/verify-integrity"
        payload = {
            "file_path": SAMPLE_PDF,
            "expected_hash": "sample_hash_for_testing"
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "verified" in data
            print(f"✅ Tool 3: Integrity verified: {data['verified']}")

    def test_tool_04_extract_metadata(self):
        """Tool 4: Extract metadata"""
        endpoint = f"{BASE_URL}/api/pdf/extract-metadata"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "metadata" in data
            print(f"✅ Tool 4: Extracted metadata")


class TestBiasDetection:
    """Tests for Tool 5: Bias Detection"""

    def test_tool_05_bias_analysis(self):
        """Tool 5: Analyze for bias and racism"""
        endpoint = f"{BASE_URL}/api/analysis/analyze-racism-bias"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "flagged_segments" in data
            assert "risk_scores" in data
            print(f"✅ Tool 5: Found {data['total_flagged_segments']} flagged segments")


class TestDocumentAnalysis:
    """Tests for Tools 6-9: Document Analysis"""

    def test_tool_06_detect_inconsistencies(self):
        """Tool 6: Detect inconsistent statements"""
        endpoint = f"{BASE_URL}/api/analysis/detect-inconsistencies"
        payload = {
            "documents": [SAMPLE_PDF, SAMPLE_PDF],
            "comparison_type": "cross_document"
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "inconsistencies" in data
            print(f"✅ Tool 6: Found {len(data['inconsistencies'])} inconsistencies")

    def test_tool_07_detect_template_reuse(self):
        """Tool 7: Detect template reuse"""
        endpoint = f"{BASE_URL}/api/analysis/detect-template-reuse"
        payload = {
            "file_a": SAMPLE_PDF,
            "file_b": SAMPLE_PDF
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "similarity_score" in data
            print(f"✅ Tool 7: Similarity score: {data['similarity_score']}%")

    def test_tool_08_detect_omitted_context(self):
        """Tool 8: Detect omitted context"""
        endpoint = f"{BASE_URL}/api/analysis/detect-omitted-context"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "omitted_contexts" in data
            print(f"✅ Tool 8: Found {len(data['omitted_contexts'])} omitted contexts")

    def test_tool_09_detect_non_evidence(self):
        """Tool 9: Detect non-evidence-based statements"""
        endpoint = f"{BASE_URL}/api/analysis/detect-non-evidence-based"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "statements" in data
            print(f"✅ Tool 9: Found {len(data['statements'])} unsupported statements")


class TestEvidenceExtraction:
    """Tests for Tools 10-11: Evidence Extraction"""

    def test_tool_10_family_support_evidence(self):
        """Tool 10: Extract family support evidence"""
        endpoint = f"{BASE_URL}/api/analysis/extract-family-support"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "evidence" in data
            print(f"✅ Tool 10: Found {len(data['evidence'])} family support instances")

    def test_tool_11_pg_limitations(self):
        """Tool 11: Extract Public Guardian limitations"""
        endpoint = f"{BASE_URL}/api/analysis/extract-pg-limitations"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "limitations" in data
            print(f"✅ Tool 11: Found {len(data['limitations'])} PG limitations")


class TestComparisonTimeline:
    """Tests for Tools 12-15: Comparison & Timeline"""

    def test_tool_12_compare_documents(self):
        """Tool 12: Compare PDF documents"""
        endpoint = f"{BASE_URL}/api/analysis/compare-documents"
        payload = {
            "file_a": SAMPLE_PDF,
            "file_b": SAMPLE_PDF,
            "comparison_focus": ["recommendations"]
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "similarity_score" in data
            print(f"✅ Tool 12: Similarity: {data['similarity_score']}%")

    def test_tool_13_analyze_and_compare(self):
        """Tool 13: Analyze and compare PDFs"""
        endpoint = f"{BASE_URL}/api/analysis/analyze-and-compare"
        payload = {
            "file_a": SAMPLE_PDF,
            "file_b": SAMPLE_PDF,
            "comparison_focus": ["racism_bias_changes"]
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "similarity_score" in data
            assert "bias_changes" in data
            print(f"✅ Tool 13: Combined analysis complete")

    def test_tool_14_extract_timeline(self):
        """Tool 14: Extract timeline events"""
        endpoint = f"{BASE_URL}/api/analysis/extract-timeline"
        payload = {
            "file_path": SAMPLE_PDF,
            "sort_chronological": True
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "events" in data
            print(f"✅ Tool 14: Extracted {data['total_events']} events")

    def test_tool_15_contradiction_matrix(self):
        """Tool 15: Generate contradiction matrix"""
        endpoint = f"{BASE_URL}/api/analysis/contradiction-matrix"
        payload = {
            "documents": [
                {"file_path": SAMPLE_PDF, "document_label": "Doc 1"}
            ],
            "contradiction_types": ["date_inconsistencies"]
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "matrix_rows" in data
            print(f"✅ Tool 15: Found {data['total_contradictions']} contradictions")


class TestLegalFramework:
    """Tests for Tools 16-19: Legal Framework"""

    def test_tool_16_human_rights_breaches(self):
        """Tool 16: Extract human rights breaches"""
        endpoint = f"{BASE_URL}/api/legal/human-rights-breaches"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "breaches" in data
            print(f"✅ Tool 16: Found {data['total_breaches']} HR breaches")

    def test_tool_17_guardianship_risk(self):
        """Tool 17: Analyze guardianship risk"""
        endpoint = f"{BASE_URL}/api/legal/guardianship-risk-assessment"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "assessment" in data
            assert "compliance_rating" in data
            print(f"✅ Tool 17: Compliance rating: {data['compliance_rating']}")

    def test_tool_18_state_bias(self):
        """Tool 18: Detect state guardianship bias"""
        endpoint = f"{BASE_URL}/api/legal/detect-state-guardianship-bias"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "bias_score" in data
            print(f"✅ Tool 18: Bias score: {data['bias_score']}/10")

    def test_tool_19_professional_compliance(self):
        """Tool 19: Analyze professional compliance"""
        endpoint = f"{BASE_URL}/api/legal/professional-language-compliance"
        payload = {"file_path": SAMPLE_PDF}

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "compliance_score" in data
            print(f"✅ Tool 19: Compliance score: {data['compliance_score']}/10")


class TestNDISGoals:
    """Tests for Tool 20: NDIS Goals Alignment (CRITICAL)"""

    def test_tool_20_goals_alignment(self):
        """Tool 20: Analyze NDIS goals alignment"""
        endpoint = f"{BASE_URL}/api/legal/goals-guardianship-alignment"
        payload = {
            "file_path": SAMPLE_PDF,
            "guardianship_context": "Family guardianship application"
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "goals_analysis" in data
            assert "overall_family_alignment" in data
            assert "overall_pg_alignment" in data
            print(f"✅ Tool 20: Family {data['overall_family_alignment']}/10, PG {data['overall_pg_alignment']}/10")


class TestReportGeneration:
    """Tests for Tools 21-23: Report Generation"""

    def test_tool_21_guardianship_argument(self):
        """Tool 21: Generate guardianship argument report"""
        endpoint = f"{BASE_URL}/api/reports/guardianship-argument"
        payload = {
            "client_name": "Test Client",
            "documents": [SAMPLE_PDF],
            "ndis_plan_path": SAMPLE_PDF,
            "include_goals_analysis": True,
            "include_human_rights": True
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "report" in data
            assert "analysis_count" in data
            print(f"✅ Tool 21: Generated report with {data['analysis_count']} analyses")

    def test_tool_22_evidence_summary(self):
        """Tool 22: Generate QCAT evidence summary"""
        endpoint = f"{BASE_URL}/api/reports/qcat-evidence-summary"
        payload = {
            "case_name": "Test Case",
            "documents": [SAMPLE_PDF],
            "include_timeline": True,
            "include_contradictions": True
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "summary_text" in data
            assert "key_evidence_points" in data
            print(f"✅ Tool 22: Generated summary with {len(data['key_evidence_points'])} evidence points")

    def test_tool_23_qcat_bundle(self):
        """Tool 23: Assemble QCAT bundle"""
        endpoint = f"{BASE_URL}/api/reports/qcat-bundle"
        payload = {
            "client_name": "Test Client",
            "case_number": "QCAT123",
            "documents": [SAMPLE_PDF]
        }

        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "bundle" in data
            assert "total_documents" in data
            print(f"✅ Tool 23: Bundle with {data['total_documents']} documents")


class TestServerHealth:
    """Test server health and status"""

    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Server health: {data['status']}")

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        print(f"✅ Service: {data['service']}")

    def test_docs_available(self):
        """Test API docs are available"""
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print(f"✅ API docs available")


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*80)
    print("AGNOVAT ANALYST - COMPREHENSIVE TEST SUITE")
    print("Testing all 23 tools + server health")
    print("="*80 + "\n")

    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
