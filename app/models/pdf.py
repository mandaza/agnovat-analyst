"""
PDF processing models
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.base import DocumentStats, DocumentMetadata, PageText, TimestampedHash


class PDFExtractionRequest(BaseModel):
    """Request model for PDF text extraction"""

    file_path: str = Field(..., description="Path to PDF file")
    extract_metadata: bool = Field(default=True, description="Extract metadata")
    page_range: Optional[tuple[int, int]] = Field(
        None, description="Optional page range (start, end)"
    )


class PDFExtractionResponse(BaseModel):
    """Response model for PDF text extraction"""

    full_text: str = Field(..., description="Complete extracted text")
    pages: List[PageText] = Field(..., description="Page-by-page text content")
    stats: DocumentStats = Field(..., description="Document statistics")
    metadata: Optional[DocumentMetadata] = Field(None, description="Document metadata")
    file_path: str = Field(..., description="Path to processed file")


class DocumentHashRequest(BaseModel):
    """Request model for document hashing"""

    file_path: str = Field(..., description="Path to document")


class DocumentHashResponse(TimestampedHash):
    """Response model for document hashing"""

    pass


class DocumentVerificationRequest(BaseModel):
    """Request model for document integrity verification"""

    file_path: str = Field(..., description="Path to document")
    expected_hash: str = Field(..., description="Expected hash value")


class PDFVerificationResponse(BaseModel):
    """Response model for document verification"""

    verified: bool = Field(..., description="Verification result")
    current_hash: str = Field(..., description="Current document hash")
    expected_hash: str = Field(..., description="Expected hash")
    file_path: str = Field(..., description="Path to verified document")
    timestamp: str = Field(..., description="Verification timestamp")
    message: str = Field(..., description="Verification message")


class PDFMetadataResponse(BaseModel):
    """Response model for PDF metadata extraction"""

    metadata: DocumentMetadata = Field(..., description="Extracted metadata")
    file_path: str = Field(..., description="Path to PDF file")
    suspicious_indicators: List[str] = Field(
        default_factory=list,
        description="Suspicious metadata indicators (backdating, etc.)",
    )
