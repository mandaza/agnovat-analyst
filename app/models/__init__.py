"""
Data models for Agnovat Analyst MCP Server
"""

from app.models.base import (
    DocumentHash,
    DocumentMetadata,
    DocumentStats,
    PageText,
    TimestampedHash,
)
from app.models.pdf import PDFExtractionResponse, PDFVerificationResponse
from app.models.analysis import (
    BiasAnalysisResponse,
    ContradictionItem,
    InconsistencyResponse,
    TemplateReuseResponse,
)
from app.models.legal import HumanRightsBreach, GuardianshipRiskAssessment
from app.models.reports import QCATEvidenceBundle, GuardianshipArgumentReport

__all__ = [
    # Base models
    "DocumentHash",
    "DocumentMetadata",
    "DocumentStats",
    "PageText",
    "TimestampedHash",
    # PDF models
    "PDFExtractionResponse",
    "PDFVerificationResponse",
    # Analysis models
    "BiasAnalysisResponse",
    "ContradictionItem",
    "InconsistencyResponse",
    "TemplateReuseResponse",
    # Legal models
    "HumanRightsBreach",
    "GuardianshipRiskAssessment",
    # Report models
    "QCATEvidenceBundle",
    "GuardianshipArgumentReport",
]
