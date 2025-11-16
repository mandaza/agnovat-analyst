# Agnovat Analyst - User Guide

**Version:** 1.0.0
**Last Updated:** November 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Tools](#using-the-tools)
4. [Workflow Examples](#workflow-examples)
5. [QCAT Appeal Process](#qcat-appeal-process)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

Agnovat Analyst is a comprehensive analysis system designed to support QCAT (Queensland Civil and Administrative Tribunal) guardianship appeals. The system provides 23 specialized tools for analyzing practitioner reports, detecting bias, extracting evidence, and generating QCAT-ready legal documents.

### What It Does

- **Analyzes** practitioner reports for bias, racism, and discrimination
- **Detects** inconsistencies, contradictions, and fabrications
- **Extracts** evidence of family capacity and support
- **Evaluates** compliance with legal frameworks (GA Act 2000, HR Act 2019)
- **Assesses** NDIS goals alignment with guardianship options
- **Generates** comprehensive legal arguments and QCAT evidence bundles

### Who It's For

- Family members preparing guardianship applications
- Legal advocates supporting QCAT appeals
- Support coordinators assisting with evidence gathering
- Anyone challenging practitioner recommendations

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Access to practitioner reports (PDF format)
- NDIS plan document (if available)
- Basic understanding of guardianship law (helpful but not required)

### Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access API Documentation:**
   Open http://localhost:8000/docs in your browser

### Quick Test

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "agnovat-analyst",
  "version": "1.0.0"
}
```

---

## Using the Tools

### Tool Categories

The 23 tools are organized into 8 categories:

1. **PDF Processing (Tools 1-4):** Basic document handling
2. **Bias Detection (Tool 5):** Racism and discrimination analysis
3. **Document Analysis (Tools 6-9):** Quality and consistency checking
4. **Evidence Extraction (Tools 10-11):** Family capacity evidence
5. **Comparison & Timeline (Tools 12-15):** Cross-document analysis
6. **Legal Framework (Tools 16-19):** Rights and compliance analysis
7. **NDIS Goals (Tool 20):** Goals alignment analysis ⭐ CRITICAL
8. **Report Generation (Tools 21-23):** QCAT-ready documents

### Basic Usage Pattern

All tools follow the same pattern:

```bash
curl -X POST "http://localhost:8000/api/{category}/{tool-name}" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'
```

### Example: Bias Detection (Tool 5)

```bash
curl -X POST "http://localhost:8000/api/analysis/analyze-racism-bias" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/practitioner_report.pdf"
  }'
```

Response includes:
- Flagged segments by category (explicit racism, implicit bias, etc.)
- Risk scores (0-10) for each category
- Context for each flagged instance
- Page numbers
- QCAT-ready narrative report

---

## Workflow Examples

### Workflow 1: Single Document Analysis

**Goal:** Analyze one practitioner report for issues

**Steps:**

1. **Extract and verify document (Tools 1-3):**
   ```bash
   # Extract text
   POST /api/pdf/extract-text

   # Generate hash for chain of custody
   POST /api/pdf/generate-hash

   # Check metadata for backdating
   POST /api/pdf/extract-metadata
   ```

2. **Run bias analysis (Tool 5):**
   ```bash
   POST /api/analysis/analyze-racism-bias
   ```

3. **Check for omitted context (Tool 8):**
   ```bash
   POST /api/analysis/detect-omitted-context
   ```

4. **Extract family evidence (Tool 10):**
   ```bash
   POST /api/analysis/extract-family-support
   ```

5. **Identify human rights breaches (Tool 16):**
   ```bash
   POST /api/legal/human-rights-breaches
   ```

### Workflow 2: Multi-Document Comparison

**Goal:** Compare multiple versions of a report

**Steps:**

1. **Compare documents (Tool 12):**
   ```bash
   POST /api/analysis/compare-documents
   {
     "file_a": "report_v1.pdf",
     "file_b": "report_v2.pdf",
     "comparison_focus": ["recommendations", "risk_assessments"]
   }
   ```

2. **Analyze bias changes (Tool 13):**
   ```bash
   POST /api/analysis/analyze-and-compare
   ```

3. **Generate contradiction matrix (Tool 15):**
   ```bash
   POST /api/analysis/contradiction-matrix
   {
     "documents": [
       {"file_path": "report1.pdf", "document_label": "Jan 2023"},
       {"file_path": "report2.pdf", "document_label": "Jun 2023"}
     ]
   }
   ```

### Workflow 3: Complete QCAT Submission

**Goal:** Create full evidence bundle for tribunal

**Steps:**

1. **Analyze NDIS goals alignment (Tool 20):** ⭐ CRITICAL
   ```bash
   POST /api/legal/goals-guardianship-alignment
   {
     "file_path": "ndis_plan.pdf",
     "guardianship_context": "Family guardianship application"
   }
   ```

2. **Generate guardianship argument (Tool 21):**
   ```bash
   POST /api/reports/guardianship-argument
   {
     "client_name": "Client Name",
     "documents": ["report1.pdf", "report2.pdf"],
     "ndis_plan_path": "ndis_plan.pdf",
     "include_goals_analysis": true,
     "include_human_rights": true
   }
   ```

3. **Create evidence summary (Tool 22):**
   ```bash
   POST /api/reports/qcat-evidence-summary
   {
     "case_name": "Smith Guardianship Application",
     "documents": ["report1.pdf", "report2.pdf"],
     "include_timeline": true,
     "include_contradictions": true
   }
   ```

4. **Assemble complete bundle (Tool 23):**
   ```bash
   POST /api/reports/qcat-bundle
   {
     "client_name": "Client Name",
     "case_number": "GAA123/2024",
     "documents": ["report1.pdf", "report2.pdf", "ndis_plan.pdf"]
   }
   ```

---

## QCAT Appeal Process

### Understanding the Goal

The Agnovat Analyst system helps you build a strong case for **family guardianship** instead of **Public Guardian** appointment by providing:

1. **Evidence of bias** in practitioner assessments
2. **Documentation of family capacity** and support
3. **Legal framework compliance** analysis
4. **NDIS goals alignment** showing family option better supports client
5. **QCAT-ready documents** for tribunal submission

### Key Legal Arguments

The system helps you demonstrate:

#### 1. Guardianship and Administration Act 2000 (Qld) Compliance

**General Principle 1: Least Restrictive Option**
- Tool 17 (Guardianship Risk Assessment) evaluates restrictiveness
- Tool 20 (NDIS Goals) shows family option supports independence

**General Principle 5: Will and Preferences**
- Tool 20 (NDIS Goals) demonstrates family alignment with client wishes
- Tool 8 (Omitted Context) shows practitioner ignored client preferences

**General Principle 3: Maintain Relationships**
- Tool 10 (Family Evidence) documents existing supportive relationships
- Tool 14 (Timeline) shows sustained family involvement

#### 2. Human Rights Act 2019 (Qld) Protection

- Tool 16 identifies breaches of fundamental rights
- Section 26 (family protection) violations
- Section 28 (cultural rights) violations

#### 3. Evidence Reliability Challenges

- Tool 15 (Contradiction Matrix) undermines practitioner credibility
- Tool 6 (Inconsistencies) shows unreliable evidence
- Tool 18 (State Bias) demonstrates practitioner bias

### Building Your Case

**Phase 1: Evidence Collection** (Weeks 1-2)
- Gather all practitioner reports
- Obtain NDIS plan
- Collect family support documentation

**Phase 2: Analysis** (Week 3)
- Run Tools 1-20 on all documents
- Document all findings
- Identify strongest evidence

**Phase 3: Report Generation** (Week 4)
- Generate guardianship argument (Tool 21)
- Create evidence summary (Tool 22)
- Assemble complete bundle (Tool 23)

**Phase 4: QCAT Submission** (Week 5)
- Review generated reports
- Submit to QCAT
- Prepare for hearing

---

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### 2. File Not Found Errors

**Error:** `404: File not found`

**Solution:**
- Use absolute paths: `/full/path/to/file.pdf`
- Check file exists: `ls /path/to/file.pdf`
- Verify file is readable

#### 3. PDF Extraction Fails

**Error:** PDF cannot be read

**Solution:**
- Ensure PDF is not corrupted
- Check PDF is not password-protected
- Try re-saving PDF with different software

#### 4. Analysis Returns Empty Results

**Cause:** Document doesn't contain target patterns

**Solution:**
- This is normal - not all documents have bias/issues
- Check other documents
- Review patterns in service files if needed

### Getting Help

1. **Check API Documentation:** http://localhost:8000/docs
2. **Review Error Logs:** Look at console output
3. **Test with Sample Data:** Use test suite to verify setup
4. **Check GitHub Issues:** Report bugs or request features

---

## Best Practices

### Document Preparation

✅ **DO:**
- Use high-quality PDF scans
- Keep original filenames for tracking
- Maintain backup copies
- Document chain of custody

❌ **DON'T:**
- Modify source documents
- Use password-protected PDFs
- Rely on single document analysis
- Skip the hash verification (Tool 2)

### Analysis Strategy

✅ **DO:**
- Run multiple tools for comprehensive analysis
- Compare multiple document versions
- Use Tool 20 (NDIS Goals) - it's CRITICAL
- Generate reports for QCAT review

❌ **DON'T:**
- Cherry-pick favorable results only
- Ignore contradictory evidence
- Skip legal framework analysis
- Submit raw tool output to QCAT

### QCAT Submission

✅ **DO:**
- Use generated reports as foundation
- Review and customize for your case
- Include SHA-256 hashes for documents
- Cross-reference analysis findings

❌ **DON'T:**
- Submit without legal review
- Use technical jargon without explanation
- Overwhelm with every minor finding
- Ignore QCAT formatting requirements

---

## Next Steps

1. **Run Test Suite:** `python tests/test_all_tools.py`
2. **Review API Reference:** See `API_REFERENCE.md`
3. **Check Examples:** See workflow examples above
4. **Start Analysis:** Begin with your documents

---

**Support:** For questions or issues, consult the API documentation at http://localhost:8000/docs

**Legal Disclaimer:** This system provides analysis tools only. Consult qualified legal professionals for legal advice regarding QCAT proceedings.
