"""
Report Generation Tools (Tools 21-23)
QCAT argument reports, evidence summaries, and complete evidence bundles
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.reports import (
    GuardianshipArgumentRequest,
    GuardianshipArgumentResponse,
    QCATEvidenceSummaryRequest,
    QCATEvidenceSummaryResponse,
    QCATBundleRequest,
    QCATBundleResponse,
)
from app.services.report_generation_service import (
    generate_guardianship_argument_report as generate_argument_service,
    generate_qcat_evidence_summary as generate_summary_service,
    generate_qcat_bundle as generate_bundle_service,
)

router = APIRouter()


@router.post("/guardianship-argument", response_model=GuardianshipArgumentResponse)
async def generate_guardianship_argument_report(request: GuardianshipArgumentRequest):
    """
    Tool 21: Generate comprehensive guardianship argument report.

    Creates a complete legal narrative for QCAT guardianship applications, synthesizing
    analysis from multiple tools into a coherent argument.

    **Report Sections:**
    - Executive Summary
    - Grounds for Family Guardianship
    - Concerns Regarding Public Guardian
    - Legal Framework Analysis (GA Act 2000, HR Act 2019)
    - Evidence Summary
    - Risk Analysis
    - NDIS Goals Alignment
    - Conclusion and Recommendations

    **Analysis Included:**
    - NDIS goals alignment (if NDIS plan provided)
    - Bias and racism analysis
    - Human rights breach analysis
    - Family support evidence
    - Multi-domain capability assessment

    **Use Case:** Primary legal argument document for QCAT submission supporting
    family guardianship application.
    """
    try:
        logger.info(f"Generating guardianship argument report for {request.client_name}")
        logger.info(f"Documents to analyze: {len(request.documents)}")

        result = await generate_argument_service(request)

        logger.info(
            f"Argument report generated: {result.analysis_count} analyses performed, "
            f"{result.documents_analyzed} documents analyzed"
        )

        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating guardianship argument report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Guardianship argument report generation failed: {str(e)}"
        )


@router.post("/qcat-evidence-summary", response_model=QCATEvidenceSummaryResponse)
async def generate_qcat_evidence_summary(request: QCATEvidenceSummaryRequest):
    """
    Tool 22: Generate concise QCAT evidence summary.

    Creates a focused executive summary suitable for front page of QCAT evidence
    bundle, highlighting key findings and legal arguments.

    **Summary Components:**
    - Evidence overview (timeline, contradictions)
    - Key evidence points (bullet format)
    - Legal arguments (statutory basis)
    - Timeline summary (if requested)
    - Contradiction summary (if requested)

    **Optional Analysis:**
    - Timeline extraction (set include_timeline=true)
    - Contradiction matrix (set include_contradictions=true)

    **Output Format:**
    - Concise, tribunal-ready language
    - Structured for quick review
    - Highlights most compelling evidence
    - Clear legal framework references

    **Use Case:** Executive summary for QCAT members, overview of case evidence
    """
    try:
        logger.info(f"Generating QCAT evidence summary for {request.case_name}")
        logger.info(f"Documents: {len(request.documents)}")

        result = await generate_summary_service(request)

        logger.info(
            f"Evidence summary generated: {len(result.key_evidence_points)} evidence points, "
            f"{result.documents_reviewed} documents reviewed"
        )

        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating QCAT evidence summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"QCAT evidence summary generation failed: {str(e)}"
        )


@router.post("/qcat-bundle", response_model=QCATBundleResponse)
async def generate_qcat_bundle(request: QCATBundleRequest):
    """
    Tool 23: Assemble complete QCAT evidence bundle.

    Creates a comprehensive, organized evidence package ready for QCAT submission,
    including document register with integrity verification (SHA-256 hashing).

    **Bundle Components:**
    1. **Table of Contents**
       - Section index with page numbers
       - Document references
       - Appendix listings

    2. **Document Register**
       - Complete list of source documents
       - SHA-256 hash for each document (chain of custody)
       - Timestamp of hash generation
       - Document metadata (creation date, author, etc.)

    3. **Analysis Reports**
       - Bias and discrimination analysis
       - Human rights breach analysis
       - Guardianship risk assessment
       - NDIS goals alignment
       - Family capacity evidence
       - Timeline and contradictions

    4. **Supporting Evidence**
       - Documented family support instances
       - Public Guardian limitation evidence
       - Timeline of events
       - Contradiction matrix

    5. **Legal Arguments**
       - GA Act 2000 compliance
       - HR Act 2019 compliance
       - Evidence-based decision making
       - Natural justice considerations

    6. **Bundle Summary**
       - Executive overview
       - Key findings
       - Recommendation

    **Document Integrity:**
    - SHA-256 cryptographic hashing for all documents
    - Tamper-evidence through hash verification
    - Chain of custody maintenance
    - Timestamp documentation

    **Use Case:** Complete, organized submission package for QCAT tribunal,
    ensuring all evidence is properly documented and verifiable.
    """
    try:
        logger.info(f"Assembling QCAT bundle for {request.client_name}")
        logger.info(f"Bundle documents: {len(request.documents)}")

        result = await generate_bundle_service(request)

        logger.info(
            f"QCAT bundle assembled: {result.total_documents} documents, "
            f"{result.total_reports} reports, "
            f"Complete: {result.bundle_complete}"
        )

        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error assembling QCAT bundle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"QCAT bundle assembly failed: {str(e)}"
        )
