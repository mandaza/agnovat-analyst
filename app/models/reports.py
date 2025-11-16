"""
Report generation models
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """A timeline event"""

    date: datetime = Field(..., description="Event date")
    event: str = Field(..., description="Event description")
    source: str = Field(..., description="Source document/page")
    category: str = Field(..., description="Event category")
    significance: str = Field(..., description="Significance/relevance")


class TimelineExtractionRequest(BaseModel):
    """Request for timeline extraction"""

    file_path: str = Field(..., description="Path to document")


class TimelineExtractionResponse(BaseModel):
    """Response for timeline extraction"""

    file_path: str = Field(..., description="Analyzed document")
    timeline: List[TimelineEvent] = Field(..., description="Extracted timeline events")
    total_events: int = Field(..., description="Total number of events")
    date_range: tuple[Optional[datetime], Optional[datetime]] = Field(
        ..., description="Date range (start, end)"
    )


class ContradictionMatrixRequest(BaseModel):
    """Request for contradiction matrix generation"""

    documents: List[str] = Field(..., min_length=2, description="Documents to analyze")


class ContradictionMatrixRow(BaseModel):
    """A row in the contradiction matrix"""

    topic: str = Field(..., description="Event/topic")
    version_1: str = Field(..., description="Version from document 1")
    version_2: str = Field(..., description="Version from document 2")
    conflict: str = Field(..., description="Nature of conflict")
    explanation: str = Field(..., description="Detailed explanation")
    source_1: str = Field(..., description="Source reference for version 1")
    source_2: str = Field(..., description="Source reference for version 2")


class ContradictionMatrixResponse(BaseModel):
    """Response for contradiction matrix"""

    documents: List[str] = Field(..., description="Analyzed documents")
    matrix: List[ContradictionMatrixRow] = Field(..., description="Contradiction matrix")
    total_contradictions: int = Field(..., description="Total contradictions")
    summary: str = Field(..., description="Summary")


class GuardianshipArgumentRequest(BaseModel):
    """Request for guardianship argument report generation"""

    client_name: str = Field(..., description="Client name")
    documents: List[str] = Field(..., description="List of document paths to analyze")
    ndis_plan_path: Optional[str] = Field(None, description="Path to NDIS plan document")
    guardianship_context: Optional[str] = Field(None, description="Additional context")
    report_title: Optional[str] = Field(None, description="Custom report title")
    include_goals_analysis: bool = Field(default=True, description="Include NDIS goals analysis")
    include_human_rights: bool = Field(default=True, description="Include human rights analysis")
    case_number: Optional[str] = Field(None, description="QCAT case number")


class GuardianshipArgumentReport(BaseModel):
    """QCAT guardianship argument report"""

    report_title: str = Field(..., description="Report title")
    client_name: str = Field(..., description="Client name")
    report_date: str = Field(..., description="Report date")
    executive_summary: str = Field(..., description="Executive summary")
    grounds_for_family_guardianship: List[str] = Field(..., description="Grounds supporting family")
    grounds_against_pg: List[str] = Field(..., description="Concerns about PG")
    legal_framework_analysis: str = Field(..., description="Legal framework analysis")
    evidence_summary: str = Field(..., description="Evidence summary")
    risk_analysis: str = Field(..., description="Risk analysis")
    goals_alignment_summary: str = Field(..., description="NDIS goals alignment summary")
    conclusion: str = Field(..., description="Conclusion")
    recommendations: List[str] = Field(..., description="Recommendations")
    supporting_documents: List[str] = Field(..., description="List of supporting documents")


class GuardianshipArgumentResponse(BaseModel):
    """Response from guardianship argument report generation"""

    report: GuardianshipArgumentReport = Field(..., description="Generated report")
    analysis_count: int = Field(..., description="Number of analyses performed")
    documents_analyzed: int = Field(..., description="Number of documents analyzed")
    report_summary: str = Field(..., description="Brief summary")


class QCATEvidenceSummaryRequest(BaseModel):
    """Request for QCAT evidence summary"""

    case_name: str = Field(..., description="Case name/reference")
    documents: List[str] = Field(..., description="List of document paths")
    include_timeline: bool = Field(default=True, description="Include timeline analysis")
    include_contradictions: bool = Field(default=True, description="Include contradiction analysis")


class QCATEvidenceSummaryResponse(BaseModel):
    """Response from QCAT evidence summary generation"""

    summary_text: str = Field(..., description="Evidence summary text")
    key_evidence_points: List[str] = Field(..., description="Key evidence points")
    legal_arguments: List[str] = Field(..., description="Legal arguments")
    timeline_summary: str = Field(..., description="Timeline summary")
    contradiction_summary: str = Field(..., description="Contradiction summary")
    documents_reviewed: int = Field(..., description="Number of documents reviewed")


class QCATBundleRequest(BaseModel):
    """Request for QCAT evidence bundle generation"""

    client_name: str = Field(..., description="Client name")
    case_number: Optional[str] = Field(None, description="QCAT case number")
    documents: List[str] = Field(..., description="Supporting document paths")
    bundle_title: Optional[str] = Field(None, description="Custom bundle title")


class QCATEvidenceBundle(BaseModel):
    """Complete QCAT evidence bundle"""

    bundle_title: str = Field(..., description="Bundle title")
    client_name: str = Field(..., description="Client name")
    case_number: Optional[str] = Field(None, description="QCAT case number")
    bundle_date: str = Field(..., description="Bundle creation date")
    table_of_contents: List[Dict] = Field(..., description="Table of contents")
    document_register: List[Dict] = Field(..., description="Document register with hashes")
    analysis_reports: List[str] = Field(..., description="List of analysis reports included")
    supporting_evidence: List[str] = Field(..., description="List of supporting evidence")
    legal_arguments: List[str] = Field(..., description="Legal arguments")
    bundle_summary: str = Field(..., description="Bundle summary")


class QCATBundleResponse(BaseModel):
    """Response from QCAT bundle generation"""

    bundle: QCATEvidenceBundle = Field(..., description="Generated bundle")
    total_documents: int = Field(..., description="Total documents in bundle")
    total_reports: int = Field(..., description="Total reports in bundle")
    bundle_complete: bool = Field(..., description="Bundle completion status")
    bundle_summary: str = Field(..., description="Brief summary")


class ComparisonReportRequest(BaseModel):
    """Request for document comparison report"""

    file_a: str = Field(..., description="First document path")
    file_b: str = Field(..., description="Second document path")
    document_a_label: str = Field(default="Document A", description="Label for document A")
    document_b_label: str = Field(default="Document B", description="Label for document B")


class DocumentDifference(BaseModel):
    """A difference between two documents"""

    category: str = Field(..., description="Difference category")
    description: str = Field(..., description="Description of difference")
    document_a_content: str = Field(..., description="Content from document A")
    document_b_content: str = Field(..., description="Content from document B")
    page_a: Optional[int] = Field(None, description="Page in document A")
    page_b: Optional[int] = Field(None, description="Page in document B")
    significance: str = Field(..., description="Significance level")


class ComparisonReportResponse(BaseModel):
    """Response for document comparison"""

    document_a: str = Field(..., description="Document A path")
    document_b: str = Field(..., description="Document B path")
    similarity_score: float = Field(..., ge=0.0, le=100.0, description="Overall similarity %")
    differences: List[DocumentDifference] = Field(..., description="Detected differences")
    unique_content_a: List[str] = Field(..., description="Content unique to document A")
    unique_content_b: List[str] = Field(..., description="Content unique to document B")
    diff_summary: str = Field(..., description="Summary of differences")
    narrative_report: str = Field(..., description="Narrative comparison report")
