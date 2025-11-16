"""
Document Analysis Tools (Tools 5-15)
Bias detection, inconsistencies, template reuse, evidence extraction, comparisons
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.analysis import (
    BiasAnalysisRequest,
    BiasAnalysisResponse,
    InconsistencyRequest,
    InconsistencyResponse,
    TemplateReuseRequest,
    TemplateReuseResponse,
    OmittedContextRequest,
    OmittedContextResponse,
    NonEvidenceBasedRequest,
    NonEvidenceBasedResponse,
    FamilySupportEvidenceRequest,
    FamilySupportEvidenceResponse,
)
from app.models.reports import (
    ComparisonReportRequest,
    ComparisonReportResponse,
    TimelineExtractionRequest,
    TimelineExtractionResponse,
    ContradictionMatrixRequest,
    ContradictionMatrixResponse,
)
from app.services.nlp_service import analyze_for_bias_and_racism
from app.services.document_analysis_service import (
    detect_inconsistent_statements as detect_inconsistencies_service,
    detect_template_reuse as detect_template_reuse_service,
    detect_omitted_context as detect_omitted_context_service,
    detect_non_evidence_based_statements as detect_non_evidence_service,
)
from app.services.evidence_extraction_service import (
    extract_family_support_evidence as extract_family_support_service,
    extract_public_guardian_limitations as extract_pg_limitations_service,
)
from app.services.comparison_timeline_service import (
    compare_pdf_documents as compare_documents_service,
    analyze_and_compare_pdfs as analyze_compare_service,
    extract_timeline_events as extract_timeline_service,
    generate_contradiction_matrix as generate_matrix_service,
)

router = APIRouter()


@router.post("/analyze-racism-bias", response_model=BiasAnalysisResponse)
async def analyze_pdf_for_racism(request: BiasAnalysisRequest):
    """
    Tool 5: Detect explicit racism, implicit bias, cultural insensitivity, and stigmatizing language.

    Analyzes document for discriminatory content including explicit and implicit bias,
    cultural insensitivity, and stigmatizing language.

    **Use Case:** Showing discriminatory reporting for QCAT appeals.
    """
    try:
        logger.info(f"Analyzing document for bias: {request.file_path}")
        result = await analyze_for_bias_and_racism(request)
        logger.info(f"Bias analysis complete: {len(result.flagged_segments)} segments flagged")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error in bias analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bias analysis failed: {str(e)}")


@router.post("/detect-inconsistencies", response_model=InconsistencyResponse)
async def detect_inconsistent_statements(request: InconsistencyRequest):
    """
    Tool 6: Identify contradictions across one or more practitioner documents.

    Detects contradictions including inconsistent dates, different versions of events,
    and changed severity levels across multiple reports.

    **Use Case:** Discrediting practitioner reliability.
    """
    try:
        logger.info(f"Detecting inconsistencies across {len(request.documents)} documents")
        result = await detect_inconsistencies_service(request)
        logger.info(f"Found {len(result.contradictions)} contradictions")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error detecting inconsistencies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inconsistency detection failed: {str(e)}")


@router.post("/detect-template-reuse", response_model=TemplateReuseResponse)
async def detect_template_reuse_and_copying(request: TemplateReuseRequest):
    """
    Tool 7: Detect copy/paste text used across multiple clients or reports.

    Identifies matching text blocks and calculates similarity percentages
    to prove assessments are generic or fabricated.

    **Use Case:** Proving assessments are generic or fabricated.
    """
    try:
        logger.info(f"Detecting template reuse across {len(request.documents)} documents")
        result = await detect_template_reuse_service(request)
        logger.info(f"Found {len(result.matching_blocks)} matching blocks, {result.percentage_similarity:.1f}% similarity")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error detecting template reuse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template reuse detection failed: {str(e)}")


@router.post("/detect-omitted-context", response_model=OmittedContextResponse)
async def detect_omitted_context(request: OmittedContextRequest):
    """
    Tool 8: Identify missing context such as antecedents, triggers, positive behaviours.

    Detects missing context including antecedents, triggers, positive behaviors,
    and family involvement that should have been documented.

    **Use Case:** Demonstrating biased, one-sided reporting.
    """
    try:
        logger.info(f"Detecting omitted context in: {request.file_path}")
        result = await detect_omitted_context_service(request)
        logger.info(f"Found {len(result.missing_context_items)} omitted context items")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error detecting omitted context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Omitted context detection failed: {str(e)}")


@router.post("/detect-non-evidence-based", response_model=NonEvidenceBasedResponse)
async def detect_non_evidence_based_statements(request: NonEvidenceBasedRequest):
    """
    Tool 9: Flag statements with no evidence, dates, or examples.

    Identifies unsupported claims like "the client is always aggressive"
    that lack specific evidence or documentation.

    **Use Case:** Challenging validity of practitioner conclusions.
    """
    try:
        logger.info(f"Detecting non-evidence-based statements in: {request.file_path}")
        result = await detect_non_evidence_service(request)
        logger.info(f"Found {len(result.unsupported_claims)} unsupported claims, justification score: {result.justification_score:.1f}/10")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error detecting non-evidence-based statements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Non-evidence-based statement detection failed: {str(e)}")


@router.post("/extract-family-support", response_model=FamilySupportEvidenceResponse)
async def extract_family_support_evidence(request: FamilySupportEvidenceRequest):
    """
    Tool 10: Identify all mentions of family involvement and support.

    Extracts evidence of family involvement across emotional, community,
    daily living, cultural, and employment domains.

    **Use Case:** Showing parents are supportive and capable.
    """
    try:
        logger.info(f"Extracting family support evidence from: {request.file_path}")
        result = await extract_family_support_service(request)
        logger.info(f"Found {result.total_instances} family support instances")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error extracting family support evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Family support extraction failed: {str(e)}")


@router.post("/extract-pg-limitations", response_model=FamilySupportEvidenceResponse)
async def extract_public_guardian_limitations(request: FamilySupportEvidenceRequest):
    """
    Tool 11: Identify risks or negative impacts from Public Guardian oversight.

    Extracts evidence of limitations and negative impacts created by
    Public Guardian appointment.

    **Use Case:** Showing Public Guardian may not align with client needs.
    """
    try:
        logger.info(f"Extracting Public Guardian limitations from: {request.file_path}")
        result = await extract_pg_limitations_service(request)
        logger.info(f"Found {result.total_instances} Public Guardian limitation instances")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error extracting Public Guardian limitations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Public Guardian limitation extraction failed: {str(e)}")


@router.post("/compare-documents", response_model=ComparisonReportResponse)
async def compare_pdf_documents(request: ComparisonReportRequest):
    """
    Tool 12: Compare two practitioner reports and highlight differences.

    Performs detailed comparison highlighting changed recommendations,
    new claims, and altered assessments.

    **Use Case:** Showing changed recommendations or new claims.
    """
    try:
        logger.info(f"Comparing documents: {request.file_a} vs {request.file_b}")
        result = await compare_documents_service(request)
        logger.info(f"Comparison complete: {result.similarity_score:.1f}% similar, {len(result.differences)} differences")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document comparison failed: {str(e)}")


@router.post("/analyze-and-compare", response_model=ComparisonReportResponse)
async def analyze_and_compare_pdfs(request: ComparisonReportRequest):
    """
    Tool 13: Full analysis + comparison of two documents in a single tool.

    Combined racism, bias, fabrication analysis with document comparison.

    **Use Case:** Identifying changes used to justify guardianship transfer.
    """
    try:
        logger.info(f"Analyzing and comparing: {request.file_a} vs {request.file_b}")
        result = await analyze_compare_service(request)
        logger.info(f"Analysis and comparison complete")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze and compare: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis and comparison failed: {str(e)}")


@router.post("/extract-timeline", response_model=TimelineExtractionResponse)
async def extract_timeline_events(request: TimelineExtractionRequest):
    """
    Tool 14: Extract all date+event pairs to build a timeline.

    Creates chronological timeline from date and event mentions in documents.

    **Use Case:** Showing patterns of involvement or misreporting.
    """
    try:
        logger.info(f"Extracting timeline from: {request.file_path}")
        result = await extract_timeline_service(request)
        logger.info(f"Timeline extraction complete: {result.total_events} events found")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error extracting timeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Timeline extraction failed: {str(e)}")


@router.post("/contradiction-matrix", response_model=ContradictionMatrixResponse)
async def generate_contradiction_matrix(request: ContradictionMatrixRequest):
    """
    Tool 15: Create structured contradictions table.

    Generates table with rows showing: event/topic | version1 | version2 | conflict | explanation

    **Use Case:** Highlighting unreliable practitioner evidence.
    """
    try:
        logger.info(f"Generating contradiction matrix for {len(request.documents)} documents")
        result = await generate_matrix_service(request)
        logger.info(f"Matrix generated: {result.total_contradictions} contradictions found")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating contradiction matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contradiction matrix generation failed: {str(e)}")
