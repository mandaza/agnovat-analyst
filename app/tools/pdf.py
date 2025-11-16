"""
PDF Processing Tools (Tools 1-4)
- extract_pdf_text
- generate_document_hash
- verify_document_integrity
- extract_metadata_and_timestamps
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
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
from app.services.pdf_service import (
    extract_text_from_pdf,
    generate_hash,
    verify_integrity,
    extract_metadata,
)

router = APIRouter()


@router.post("/extract-text", response_model=PDFExtractionResponse)
async def extract_pdf_text(request: PDFExtractionRequest):
    """
    Tool 1: Extract full text, page-by-page text, and document statistics from a PDF.

    This tool extracts all text content from a PDF document, providing both
    complete text and page-by-page breakdowns with statistics.

    **Use Case:** Foundation for all downstream analysis tools.
    """
    try:
        logger.info(f"Extracting text from PDF: {request.file_path}")
        result = await extract_text_from_pdf(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"PDF file not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF text: {str(e)}")


@router.post("/generate-hash", response_model=DocumentHashResponse)
async def generate_document_hash(request: DocumentHashRequest):
    """
    Tool 2: Create SHA-256 hash of the PDF for integrity and evidence chain-of-custody.

    Generates a cryptographic hash to ensure document integrity and maintain
    proper chain of custody for legal proceedings.

    **Use Case:** Ensuring evidence has not been altered.
    """
    try:
        logger.info(f"Generating hash for document: {request.file_path}")
        result = await generate_hash(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error generating hash: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate hash: {str(e)}")


@router.post("/verify-integrity", response_model=PDFVerificationResponse)
async def verify_document_integrity(request: DocumentVerificationRequest):
    """
    Tool 3: Confirm PDF has not been modified since submission.

    Verifies that a document's current hash matches the expected hash,
    confirming no modifications have occurred.

    **Use Case:** QCAT admissibility and evidence integrity.
    """
    try:
        logger.info(f"Verifying integrity of document: {request.file_path}")
        result = await verify_integrity(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error verifying integrity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify integrity: {str(e)}")


@router.post("/extract-metadata", response_model=PDFMetadataResponse)
async def extract_metadata_and_timestamps(request: PDFExtractionRequest):
    """
    Tool 4: Extract metadata such as creation date, modification date, author.

    Extracts PDF metadata including timestamps, author information, and software used.
    Also flags suspicious indicators like backdated documents.

    **Use Case:** Detecting backdated or suspicious documents.
    """
    try:
        logger.info(f"Extracting metadata from: {request.file_path}")
        result = await extract_metadata(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract metadata: {str(e)}")
