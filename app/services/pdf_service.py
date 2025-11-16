"""
PDF Processing Service
Handles PDF extraction, hashing, verification, and metadata extraction
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

import PyPDF2
import pdfplumber
from loguru import logger

from app.models.pdf import (
    PDFExtractionRequest,
    PDFExtractionResponse,
    DocumentHashRequest,
    DocumentHashResponse,
    DocumentVerificationRequest,
    PDFVerificationResponse,
    PDFMetadataResponse,
)
from app.models.base import DocumentStats, DocumentMetadata, PageText
from app.config import settings


async def extract_text_from_pdf(request: PDFExtractionRequest) -> PDFExtractionResponse:
    """
    Extract text from PDF using pdfplumber for better accuracy.

    Args:
        request: PDFExtractionRequest with file path and options

    Returns:
        PDFExtractionResponse with full text, pages, and statistics
    """
    file_path = Path(request.file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    pages_data = []
    full_text = ""
    total_words = 0
    total_chars = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)

            # Check max pages limit
            if page_count > settings.PDF_MAX_PAGES:
                logger.warning(f"PDF exceeds max pages ({settings.PDF_MAX_PAGES})")

            # Extract page by page
            for page_num, page in enumerate(pdf.pages, start=1):
                # Handle page range if specified
                if request.page_range:
                    start, end = request.page_range
                    if page_num < start or page_num > end:
                        continue

                page_text = page.extract_text() or ""
                word_count = len(page_text.split())
                char_count = len(page_text)

                pages_data.append(
                    PageText(
                        page_number=page_num,
                        text=page_text,
                        word_count=word_count,
                        char_count=char_count,
                    )
                )

                full_text += page_text + "\n\n"
                total_words += word_count
                total_chars += char_count

        # Calculate statistics
        stats = DocumentStats(
            page_count=len(pages_data),
            word_count=total_words,
            char_count=total_chars,
            avg_words_per_page=total_words / len(pages_data) if pages_data else 0,
        )

        # Extract metadata if requested
        metadata = None
        if request.extract_metadata:
            metadata_response = await extract_metadata(request)
            metadata = metadata_response.metadata

        return PDFExtractionResponse(
            full_text=full_text.strip(),
            pages=pages_data,
            stats=stats,
            metadata=metadata,
            file_path=str(file_path),
        )

    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise


async def generate_hash(request: DocumentHashRequest) -> DocumentHashResponse:
    """
    Generate SHA-256 hash for document integrity.

    Args:
        request: DocumentHashRequest with file path

    Returns:
        DocumentHashResponse with hash, timestamp, and file info
    """
    file_path = Path(request.file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Read file and generate hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        file_size = file_path.stat().st_size

        return DocumentHashResponse(
            hash=sha256_hash.hexdigest(),
            algorithm=settings.HASH_ALGORITHM,
            file_path=str(file_path),
            timestamp=datetime.now(),
            file_size=file_size,
        )

    except Exception as e:
        logger.error(f"Error generating hash: {str(e)}")
        raise


async def verify_integrity(request: DocumentVerificationRequest) -> PDFVerificationResponse:
    """
    Verify document integrity by comparing hashes.

    Args:
        request: DocumentVerificationRequest with file path and expected hash

    Returns:
        PDFVerificationResponse with verification result
    """
    try:
        # Generate current hash
        hash_request = DocumentHashRequest(file_path=request.file_path)
        current_hash_response = await generate_hash(hash_request)

        current_hash = current_hash_response.hash
        expected_hash = request.expected_hash.lower()
        verified = current_hash.lower() == expected_hash

        message = (
            "Document integrity verified successfully"
            if verified
            else "Document integrity verification FAILED - hashes do not match"
        )

        return PDFVerificationResponse(
            verified=verified,
            current_hash=current_hash,
            expected_hash=expected_hash,
            file_path=request.file_path,
            timestamp=current_hash_response.timestamp.isoformat(),
            message=message,
        )

    except Exception as e:
        logger.error(f"Error verifying integrity: {str(e)}")
        raise


async def extract_metadata(request: PDFExtractionRequest) -> PDFMetadataResponse:
    """
    Extract PDF metadata including creation/modification dates and author info.

    Args:
        request: PDFExtractionRequest with file path

    Returns:
        PDFMetadataResponse with metadata and suspicious indicators
    """
    file_path = Path(request.file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    suspicious_indicators = []

    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            pdf_info = pdf_reader.metadata

            # Extract metadata fields
            created = None
            modified = None
            author = None
            producer = None
            title = None
            subject = None
            creator = None

            if pdf_info:
                # Parse dates
                if pdf_info.get("/CreationDate"):
                    created = _parse_pdf_date(pdf_info["/CreationDate"])
                if pdf_info.get("/ModDate"):
                    modified = _parse_pdf_date(pdf_info["/ModDate"])

                author = pdf_info.get("/Author")
                producer = pdf_info.get("/Producer")
                title = pdf_info.get("/Title")
                subject = pdf_info.get("/Subject")
                creator = pdf_info.get("/Creator")

            # Check for suspicious indicators
            if created and modified:
                if modified < created:
                    suspicious_indicators.append(
                        "Modification date is earlier than creation date"
                    )

            file_stat = file_path.stat()
            file_modified = datetime.fromtimestamp(file_stat.st_mtime)

            if modified and abs((file_modified - modified).days) > 365:
                suspicious_indicators.append(
                    "Large discrepancy between file system and PDF metadata dates"
                )

            if not author and not creator:
                suspicious_indicators.append("No author or creator information present")

            metadata = DocumentMetadata(
                created=created,
                modified=modified,
                author=author,
                producer=producer,
                title=title,
                subject=subject,
                creator=creator,
            )

            return PDFMetadataResponse(
                metadata=metadata,
                file_path=str(file_path),
                suspicious_indicators=suspicious_indicators,
            )

    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        raise


def _parse_pdf_date(date_str: str) -> Optional[datetime]:
    """
    Parse PDF date format (D:YYYYMMDDHHmmSS) to datetime.

    Args:
        date_str: PDF date string

    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Remove D: prefix if present
        if date_str.startswith("D:"):
            date_str = date_str[2:]

        # Take first 14 characters (YYYYMMDDHHmmSS)
        date_str = date_str[:14]

        return datetime.strptime(date_str, "%Y%m%d%H%M%S")
    except Exception:
        return None
