"""
Document analysis models
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.base import FlaggedSegment, RiskScore, EvidenceItem


class BiasAnalysisRequest(BaseModel):
    """Request model for racism and bias analysis"""

    file_path: str = Field(..., description="Path to PDF document")
    client_name: Optional[str] = Field(None, description="Client name for context")


class BiasAnalysisResponse(BaseModel):
    """Response model for racism and bias analysis"""

    file_path: str = Field(..., description="Analyzed document path")
    risk_scores: Dict[str, RiskScore] = Field(..., description="Risk scores by category")
    flagged_segments: List[FlaggedSegment] = Field(..., description="Flagged text segments")
    narrative_report: str = Field(..., description="Narrative analysis report")
    overall_severity: str = Field(..., description="Overall severity: low, medium, high, critical")
    categories_detected: List[str] = Field(..., description="Bias categories detected")


class InconsistencyRequest(BaseModel):
    """Request model for inconsistency detection"""

    documents: List[str] = Field(..., min_length=2, description="Paths to documents to compare")


class ContradictionItem(BaseModel):
    """A detected contradiction between documents"""

    topic: str = Field(..., description="Topic or subject of contradiction")
    document_1_statement: str = Field(..., description="Statement from document 1")
    document_2_statement: str = Field(..., description="Statement from document 2")
    document_1_page: int = Field(..., description="Page in document 1")
    document_2_page: int = Field(..., description="Page in document 2")
    severity: str = Field(..., description="Severity: low, medium, high")
    explanation: str = Field(..., description="Explanation of the contradiction")


class InconsistencyResponse(BaseModel):
    """Response model for inconsistency detection"""

    documents: List[str] = Field(..., description="Analyzed documents")
    contradictions: List[ContradictionItem] = Field(..., description="Detected contradictions")
    severity_flag: str = Field(..., description="Overall severity")
    summary: str = Field(..., description="Summary of findings")


class TemplateReuseRequest(BaseModel):
    """Request model for template reuse detection"""

    documents: List[str] = Field(..., min_length=2, description="Documents to analyze")


class MatchingBlock(BaseModel):
    """A block of matching text across documents"""

    text: str = Field(..., description="Matching text content")
    documents: List[str] = Field(..., description="Documents containing this text")
    pages: Dict[str, int] = Field(..., description="Page numbers per document")
    length: int = Field(..., description="Length of matching block")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")


class TemplateReuseResponse(BaseModel):
    """Response model for template reuse detection"""

    documents: List[str] = Field(..., description="Analyzed documents")
    matching_blocks: List[MatchingBlock] = Field(..., description="Detected matching blocks")
    percentage_similarity: float = Field(..., ge=0.0, le=100.0, description="Overall similarity %")
    is_template_reused: bool = Field(..., description="Whether template reuse detected")
    severity: str = Field(..., description="Severity level")
    summary: str = Field(..., description="Analysis summary")


class OmittedContextRequest(BaseModel):
    """Request model for omitted context detection"""

    file_path: str = Field(..., description="Path to document")


class OmittedContextItem(BaseModel):
    """An item of omitted context"""

    category: str = Field(..., description="Category of omission")
    description: str = Field(..., description="Description of what was omitted")
    page_number: Optional[int] = Field(None, description="Relevant page number")
    impact: str = Field(..., description="Impact of the omission")
    severity: str = Field(..., description="Severity: low, medium, high")


class OmittedContextResponse(BaseModel):
    """Response model for omitted context detection"""

    file_path: str = Field(..., description="Analyzed document")
    missing_context_items: List[OmittedContextItem] = Field(
        ..., description="Detected omissions"
    )
    omission_severity_score: float = Field(
        ..., ge=0.0, le=10.0, description="Overall omission severity 0-10"
    )
    categories: List[str] = Field(..., description="Categories of omissions")
    summary: str = Field(..., description="Analysis summary")


class NonEvidenceBasedRequest(BaseModel):
    """Request for non-evidence-based statement detection"""

    file_path: str = Field(..., description="Path to document")


class UnsupportedClaim(BaseModel):
    """An unsupported or non-evidence-based claim"""

    statement: str = Field(..., description="The unsupported statement")
    page_number: int = Field(..., description="Page number")
    reason: str = Field(..., description="Why it lacks evidence")
    severity: str = Field(..., description="Severity level")
    suggested_evidence: str = Field(..., description="What evidence would be needed")


class NonEvidenceBasedResponse(BaseModel):
    """Response for non-evidence-based statement detection"""

    file_path: str = Field(..., description="Analyzed document")
    unsupported_claims: List[UnsupportedClaim] = Field(..., description="Unsupported claims")
    justification_score: float = Field(
        ..., ge=0.0, le=10.0, description="Overall justification score 0-10"
    )
    summary: str = Field(..., description="Analysis summary")


class FamilySupportEvidenceRequest(BaseModel):
    """Request for family support evidence extraction"""

    file_path: str = Field(..., description="Path to document")


class FamilySupportThemes(BaseModel):
    """Themes of family support"""

    emotional: List[EvidenceItem] = Field(default_factory=list, description="Emotional support")
    community: List[EvidenceItem] = Field(default_factory=list, description="Community support")
    daily_living: List[EvidenceItem] = Field(default_factory=list, description="Daily living")
    cultural: List[EvidenceItem] = Field(default_factory=list, description="Cultural support")
    employment: List[EvidenceItem] = Field(default_factory=list, description="Employment support")
    decision_making: List[EvidenceItem] = Field(
        default_factory=list, description="Decision-making support"
    )


class FamilySupportEvidenceResponse(BaseModel):
    """Response for family support evidence extraction"""

    file_path: str = Field(..., description="Analyzed document")
    family_support_instances: List[EvidenceItem] = Field(
        ..., description="All family support instances"
    )
    themes: FamilySupportThemes = Field(..., description="Categorized themes")
    total_instances: int = Field(..., description="Total number of instances")
    summary: str = Field(..., description="Summary of family support")
