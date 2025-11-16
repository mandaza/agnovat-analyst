"""
Base models for document processing and analysis
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class DocumentHash(BaseModel):
    """Document hash for integrity verification"""

    hash: str = Field(..., description="SHA-256 hash of the document")
    algorithm: str = Field(default="sha256", description="Hash algorithm used")
    file_path: str = Field(..., description="Path to the hashed document")


class TimestampedHash(DocumentHash):
    """Document hash with timestamp for chain of custody"""

    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp when hash was generated"
    )
    file_size: int = Field(..., description="File size in bytes")


class DocumentMetadata(BaseModel):
    """PDF document metadata"""

    created: Optional[datetime] = Field(None, description="Document creation date")
    modified: Optional[datetime] = Field(None, description="Document modification date")
    author: Optional[str] = Field(None, description="Document author")
    producer: Optional[str] = Field(None, description="PDF producer software")
    title: Optional[str] = Field(None, description="Document title")
    subject: Optional[str] = Field(None, description="Document subject")
    creator: Optional[str] = Field(None, description="Document creator application")


class DocumentStats(BaseModel):
    """Document statistics"""

    page_count: int = Field(..., description="Number of pages in document")
    word_count: int = Field(..., description="Total word count")
    char_count: int = Field(..., description="Total character count")
    avg_words_per_page: float = Field(..., description="Average words per page")


class PageText(BaseModel):
    """Text content from a single page"""

    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    text: str = Field(..., description="Extracted text content")
    word_count: int = Field(..., description="Word count for this page")
    char_count: int = Field(..., description="Character count for this page")


class FlaggedSegment(BaseModel):
    """A flagged text segment with context"""

    text: str = Field(..., description="The flagged text content")
    page_number: int = Field(..., description="Page number where segment appears")
    context: str = Field(..., description="Surrounding context")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")
    category: str = Field(..., description="Category of the issue")
    explanation: str = Field(..., description="Explanation of why this was flagged")


class EvidenceItem(BaseModel):
    """Evidence item extracted from document"""

    text: str = Field(..., description="Evidence text")
    page_number: int = Field(..., description="Page number")
    category: str = Field(..., description="Evidence category")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score 0-1")
    context: str = Field(..., description="Surrounding context")


class RiskScore(BaseModel):
    """Risk scoring structure"""

    category: str = Field(..., description="Risk category")
    score: float = Field(..., ge=0.0, le=10.0, description="Risk score 0-10")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level 0-1")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence")


class AlignmentScore(BaseModel):
    """Goal alignment scoring"""

    goal_id: str = Field(..., description="Goal identifier (e.g., G1, G2)")
    goal_name: str = Field(..., description="Goal name")
    score: float = Field(..., ge=0.0, le=10.0, description="Alignment score 0-10")
    family_support_score: float = Field(
        ..., ge=0.0, le=10.0, description="Family support score 0-10"
    )
    public_guardian_impact_score: float = Field(
        ..., ge=0.0, le=10.0, description="Public Guardian impact score 0-10"
    )
    conflicts: list[str] = Field(default_factory=list, description="Identified conflicts")
    supporting_evidence: list[str] = Field(
        default_factory=list, description="Supporting evidence"
    )
    narrative: str = Field(..., description="Narrative explanation")
