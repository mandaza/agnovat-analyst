"""
Document Analysis Service
Tools 6-9: Inconsistencies, Template Reuse, Omitted Context, Non-Evidence Statements
"""

import re
from typing import List, Dict, Set, Tuple
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict
from loguru import logger

try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    logger.warning("fuzzywuzzy not available, using basic similarity")
    FUZZYWUZZY_AVAILABLE = False

from app.models.analysis import (
    InconsistencyRequest,
    InconsistencyResponse,
    ContradictionItem,
    TemplateReuseRequest,
    TemplateReuseResponse,
    MatchingBlock,
    OmittedContextRequest,
    OmittedContextResponse,
    OmittedContextItem,
    NonEvidenceBasedRequest,
    NonEvidenceBasedResponse,
    UnsupportedClaim,
)
from app.services.pdf_service import extract_text_from_pdf
from app.models.pdf import PDFExtractionRequest
from app.config import settings


# ============================================================================
# TOOL 6: INCONSISTENCY DETECTION
# ============================================================================

class InconsistencyDetector:
    """Detects contradictions and inconsistencies across documents"""

    @staticmethod
    def extract_dates(text: str) -> List[Tuple[str, str]]:
        """Extract dates and their context from text"""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY or MM/DD/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b',
        ]

        dates_found = []
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                dates_found.append((match.group(), context))

        return dates_found

    @staticmethod
    def compare_descriptions(doc1_text: str, doc2_text: str) -> List[ContradictionItem]:
        """Compare behavioral descriptions between documents"""
        contradictions = []

        # Behavioral descriptors that should be consistent
        behaviors = [
            "aggressive", "calm", "cooperative", "uncooperative", "violent",
            "peaceful", "compliant", "non-compliant", "stable", "unstable",
            "capable", "incapable", "independent", "dependent"
        ]

        for behavior in behaviors:
            # Look for contradictory statements
            positive = f"{behavior}"
            negative_patterns = [
                f"not {behavior}",
                f"never {behavior}",
                f"rarely {behavior}",
                f"un{behavior}",
                f"non-{behavior}",
            ]

            doc1_has_positive = bool(re.search(rf'\b{positive}\b', doc1_text, re.IGNORECASE))
            doc2_has_positive = bool(re.search(rf'\b{positive}\b', doc2_text, re.IGNORECASE))

            doc1_has_negative = any(re.search(rf'\b{neg}\b', doc1_text, re.IGNORECASE) for neg in negative_patterns)
            doc2_has_negative = any(re.search(rf'\b{neg}\b', doc2_text, re.IGNORECASE) for neg in negative_patterns)

            if doc1_has_positive and doc2_has_negative:
                contradictions.append(ContradictionItem(
                    topic=f"Behavioral assessment: {behavior}",
                    document_1_statement=f"Document describes client as {behavior}",
                    document_2_statement=f"Document describes client as not {behavior}",
                    document_1_page=0,
                    document_2_page=0,
                    severity="medium",
                    explanation=f"Contradictory statements about client being {behavior}"
                ))
            elif doc1_has_negative and doc2_has_positive:
                contradictions.append(ContradictionItem(
                    topic=f"Behavioral assessment: {behavior}",
                    document_1_statement=f"Document describes client as not {behavior}",
                    document_2_statement=f"Document describes client as {behavior}",
                    document_1_page=0,
                    document_2_page=0,
                    severity="medium",
                    explanation=f"Contradictory statements about client being {behavior}"
                ))

        return contradictions


async def detect_inconsistent_statements(request: InconsistencyRequest) -> InconsistencyResponse:
    """
    Tool 6: Detect inconsistencies across multiple documents
    """
    try:
        logger.info(f"Analyzing {len(request.documents)} documents for inconsistencies")

        # Extract text from all documents
        documents_text = []
        for doc_path in request.documents:
            pdf_request = PDFExtractionRequest(file_path=doc_path, extract_metadata=False)
            pdf_result = await extract_text_from_pdf(pdf_request)
            documents_text.append({
                'path': doc_path,
                'text': pdf_result.full_text,
                'pages': pdf_result.pages
            })

        contradictions = []

        # Compare documents pairwise
        for i in range(len(documents_text)):
            for j in range(i + 1, len(documents_text)):
                doc1 = documents_text[i]
                doc2 = documents_text[j]

                # Check for date inconsistencies
                dates1 = InconsistencyDetector.extract_dates(doc1['text'])
                dates2 = InconsistencyDetector.extract_dates(doc2['text'])

                # Check for behavioral contradictions
                behavior_contradictions = InconsistencyDetector.compare_descriptions(
                    doc1['text'], doc2['text']
                )
                contradictions.extend(behavior_contradictions)

        # Determine overall severity
        if len(contradictions) > 10:
            severity_flag = "high"
        elif len(contradictions) > 5:
            severity_flag = "medium"
        else:
            severity_flag = "low"

        summary = f"Found {len(contradictions)} contradictions across {len(request.documents)} documents."

        return InconsistencyResponse(
            documents=request.documents,
            contradictions=contradictions,
            severity_flag=severity_flag,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error detecting inconsistencies: {str(e)}")
        raise


# ============================================================================
# TOOL 7: TEMPLATE REUSE DETECTION
# ============================================================================

async def detect_template_reuse(request: TemplateReuseRequest) -> TemplateReuseResponse:
    """
    Tool 7: Detect copy-paste text used across multiple reports
    """
    try:
        logger.info(f"Analyzing {len(request.documents)} documents for template reuse")

        # Extract text from all documents
        documents_text = []
        for doc_path in request.documents:
            pdf_request = PDFExtractionRequest(file_path=doc_path, extract_metadata=False)
            pdf_result = await extract_text_from_pdf(pdf_request)
            documents_text.append({
                'path': doc_path,
                'text': pdf_result.full_text,
                'pages': pdf_result.pages
            })

        matching_blocks = []

        # Compare documents pairwise for similarity
        for i in range(len(documents_text)):
            for j in range(i + 1, len(documents_text)):
                doc1 = documents_text[i]
                doc2 = documents_text[j]

                # Use sequence matcher to find matching blocks
                matcher = SequenceMatcher(None, doc1['text'], doc2['text'])

                for match in matcher.get_matching_blocks():
                    if match.size > 100:  # Only significant blocks
                        matching_text = doc1['text'][match.a:match.a + match.size]

                        # Skip if it's just whitespace or common phrases
                        if len(matching_text.strip()) > 50:
                            similarity = match.size / max(len(doc1['text']), len(doc2['text']))

                            matching_blocks.append(MatchingBlock(
                                text=matching_text[:200] + "..." if len(matching_text) > 200 else matching_text,
                                documents=[doc1['path'], doc2['path']],
                                pages={doc1['path']: 0, doc2['path']: 0},
                                length=match.size,
                                similarity=round(similarity, 3)
                            ))

        # Calculate overall similarity
        if len(documents_text) >= 2:
            total_similarity = sum(block.similarity for block in matching_blocks)
            percentage_similarity = min(100.0, (total_similarity / len(documents_text)) * 100)
        else:
            percentage_similarity = 0.0

        is_template_reused = percentage_similarity > (settings.TEMPLATE_REUSE_THRESHOLD * 100)

        if is_template_reused and percentage_similarity > 80:
            severity = "high"
        elif is_template_reused:
            severity = "medium"
        else:
            severity = "low"

        summary = (
            f"Detected {len(matching_blocks)} matching text blocks across documents. "
            f"Overall similarity: {percentage_similarity:.1f}%. "
            f"{'Significant template reuse detected.' if is_template_reused else 'No significant template reuse.'}"
        )

        return TemplateReuseResponse(
            documents=request.documents,
            matching_blocks=matching_blocks,
            percentage_similarity=round(percentage_similarity, 2),
            is_template_reused=is_template_reused,
            severity=severity,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error detecting template reuse: {str(e)}")
        raise


# ============================================================================
# TOOL 8: OMITTED CONTEXT DETECTION
# ============================================================================

class ContextAnalyzer:
    """Analyzes documents for missing context"""

    # Context elements that should be present
    REQUIRED_CONTEXT_ELEMENTS = {
        "antecedents": [
            r"\bbefore\b", r"\bprior to\b", r"\bleading up to\b",
            r"\bantecedent\b", r"\btrigger(?:ed)?\b"
        ],
        "positive_behaviors": [
            r"\bpositive\b", r"\bsuccess(?:ful)?\b", r"\bachievement\b",
            r"\bstrength\b", r"\bcapable\b", r"\bimprovement\b"
        ],
        "family_involvement": [
            r"\bfamily\b", r"\bparent(?:s)?\b", r"\bmother\b", r"\bfather\b",
            r"\bsibling\b", r"\bsupport(?:ed)?\b"
        ],
        "environmental_factors": [
            r"\benvironment\b", r"\bsetting\b", r"\bcontext\b",
            r"\bcircumstance(?:s)?\b", r"\bsituation\b"
        ],
        "client_perspective": [
            r"\bclient (?:states?|reports?|says?|feels?|believes?)\b",
            r"\bclient'?s (?:view|perspective|opinion)\b"
        ]
    }

    @staticmethod
    def check_context_presence(text: str) -> Dict[str, bool]:
        """Check which context elements are present"""
        presence = {}

        for category, patterns in ContextAnalyzer.REQUIRED_CONTEXT_ELEMENTS.items():
            found = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
            presence[category] = found

        return presence


async def detect_omitted_context(request: OmittedContextRequest) -> OmittedContextResponse:
    """
    Tool 8: Identify missing context in documents
    """
    try:
        logger.info(f"Analyzing document for omitted context: {request.file_path}")

        # Extract text
        pdf_request = PDFExtractionRequest(file_path=request.file_path, extract_metadata=False)
        pdf_result = await extract_text_from_pdf(pdf_request)

        # Check for context presence
        context_presence = ContextAnalyzer.check_context_presence(pdf_result.full_text)

        missing_context_items = []

        # Identify missing elements
        if not context_presence.get("antecedents"):
            missing_context_items.append(OmittedContextItem(
                category="antecedents",
                description="No discussion of antecedents or triggers for behaviors",
                page_number=None,
                impact="Behaviors appear without context, making them seem unprovoked",
                severity="high"
            ))

        if not context_presence.get("positive_behaviors"):
            missing_context_items.append(OmittedContextItem(
                category="positive_behaviors",
                description="No mention of positive behaviors, strengths, or successes",
                page_number=None,
                impact="Document presents only deficit-focused view of client",
                severity="high"
            ))

        if not context_presence.get("family_involvement"):
            missing_context_items.append(OmittedContextItem(
                category="family_involvement",
                description="No discussion of family involvement or support",
                page_number=None,
                impact="Family capacity and involvement are not documented",
                severity="high"
            ))

        if not context_presence.get("environmental_factors"):
            missing_context_items.append(OmittedContextItem(
                category="environmental_factors",
                description="No consideration of environmental or situational factors",
                page_number=None,
                impact="Behaviors attributed solely to client without considering context",
                severity="medium"
            ))

        if not context_presence.get("client_perspective"):
            missing_context_items.append(OmittedContextItem(
                category="client_perspective",
                description="Client's own perspective or voice not included",
                page_number=None,
                impact="Assessment is entirely third-party without client input",
                severity="high"
            ))

        # Calculate omission severity score
        omission_severity_score = (len(missing_context_items) / len(ContextAnalyzer.REQUIRED_CONTEXT_ELEMENTS)) * 10

        categories = [item.category for item in missing_context_items]

        summary = (
            f"Found {len(missing_context_items)} categories of omitted context. "
            f"Document lacks: {', '.join(categories) if categories else 'no major omissions'}."
        )

        return OmittedContextResponse(
            file_path=request.file_path,
            missing_context_items=missing_context_items,
            omission_severity_score=round(omission_severity_score, 2),
            categories=categories,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error detecting omitted context: {str(e)}")
        raise


# ============================================================================
# TOOL 9: NON-EVIDENCE-BASED STATEMENTS
# ============================================================================

class EvidenceAnalyzer:
    """Analyzes statements for evidence backing"""

    # Absolute statements without qualifiers
    ABSOLUTE_PATTERNS = [
        r"\balways\s+\w+",
        r"\bnever\s+\w+",
        r"\ball\s+(?:the\s+)?time",
        r"\bconstantly\s+\w+",
        r"\bentirely\s+\w+",
        r"\bcompletely\s+\w+",
    ]

    # Generalized statements
    GENERALIZED_PATTERNS = [
        r"\bthe\s+client\s+is\s+\w+",
        r"\bthe\s+family\s+is\s+\w+",
        r"\bthey\s+are\s+\w+",
    ]

    @staticmethod
    def has_evidence_markers(text: str, statement: str) -> bool:
        """Check if statement has evidence markers nearby"""
        evidence_markers = [
            r"\bon\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",  # dates
            r"\bat\s+\d{1,2}:\d{2}",  # times
            r"\bfor\s+example\b",
            r"\bspecifically\b",
            r"\bincluding\b",
            r"\bsuch\s+as\b",
            r"\bwitnessed\b",
            r"\bobserved\b",
            r"\bdocumented\b",
        ]

        # Get context around statement
        statement_pos = text.find(statement)
        if statement_pos == -1:
            return False

        start = max(0, statement_pos - 100)
        end = min(len(text), statement_pos + len(statement) + 100)
        context = text[start:end]

        return any(re.search(pattern, context, re.IGNORECASE) for pattern in evidence_markers)


async def detect_non_evidence_based_statements(request: NonEvidenceBasedRequest) -> NonEvidenceBasedResponse:
    """
    Tool 9: Flag statements with no evidence, dates, or examples
    """
    try:
        logger.info(f"Analyzing document for non-evidence-based statements: {request.file_path}")

        # Extract text
        pdf_request = PDFExtractionRequest(file_path=request.file_path, extract_metadata=False)
        pdf_result = await extract_text_from_pdf(pdf_request)

        unsupported_claims = []

        # Find absolute statements
        for pattern in EvidenceAnalyzer.ABSOLUTE_PATTERNS:
            for match in re.finditer(pattern, pdf_result.full_text, re.IGNORECASE):
                statement = match.group()

                # Check if it has evidence nearby
                has_evidence = EvidenceAnalyzer.has_evidence_markers(pdf_result.full_text, statement)

                if not has_evidence:
                    unsupported_claims.append(UnsupportedClaim(
                        statement=statement,
                        page_number=0,
                        reason="Absolute statement without specific dates, times, or examples",
                        severity="high",
                        suggested_evidence="Provide specific dates, times, and examples of the behavior"
                    ))

        # Find generalized statements
        for pattern in EvidenceAnalyzer.GENERALIZED_PATTERNS:
            for match in re.finditer(pattern, pdf_result.full_text, re.IGNORECASE):
                statement = match.group()

                has_evidence = EvidenceAnalyzer.has_evidence_markers(pdf_result.full_text, statement)

                if not has_evidence:
                    unsupported_claims.append(UnsupportedClaim(
                        statement=statement,
                        page_number=0,
                        reason="Generalized characterization without supporting evidence",
                        severity="medium",
                        suggested_evidence="Include specific observations with dates and context"
                    ))

        # Calculate justification score (higher is better)
        total_sentences = len(re.findall(r'[.!?]+', pdf_result.full_text))
        justification_score = max(0, 10 - (len(unsupported_claims) / max(1, total_sentences / 10)))

        summary = (
            f"Found {len(unsupported_claims)} unsupported claims. "
            f"Justification score: {justification_score:.1f}/10. "
            f"{'Document lacks evidence-based reporting.' if justification_score < 5 else 'Reasonable evidence backing.'}"
        )

        return NonEvidenceBasedResponse(
            file_path=request.file_path,
            unsupported_claims=unsupported_claims[:20],  # Limit to top 20
            justification_score=round(justification_score, 2),
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error detecting non-evidence-based statements: {str(e)}")
        raise
